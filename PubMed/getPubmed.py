import requests
import json
import os
from bs4 import BeautifulSoup
from Bio import Entrez
from urllib.parse import quote, urljoin
import time
from tqdm import tqdm

opj = os.path.join

# 配置
Entrez.email = "xxx@qq.com"  # 必须设置你的邮箱
# API_KEY = "your_api_key"  # 可选，如果有NCBI API key可以提高请求限制
# SEARCH_TERMS = ["Blood Transfusion","Transfusion Medicine","blood transfusion" ,'transfusion' ,"Organ Transplantation"]
SEARCH_TERMS = ["Omics analysis"] # 关键词列表
MAX_RESULTS = 10  # 最大获取文献数量
SAVE_DIR = "/Users/binnn/workspace/BGI/PaperCrawl/PubMed/data"  # 保存目录
OUTPUT_JSON = opj(SAVE_DIR,'pubmed_results.json')  # 输出JSON文件名
FAILED_DOWNLOADS = opj(SAVE_DIR,'failed_downloads.txt') # 保存下载失败的链接
PDF_DIR = opj(SAVE_DIR, "pdfs")  # PDF保存目录
DELAY = 0.34  # 遵守NCBI的请求频率限制(每秒不超过3次)
start_year = 2025  # 起始年份
end_year = 2026    # 结束年份

def search_pubmed(terms, max_results, API_KEY = None, start_year=None, end_year=None):
    """在PubMed上搜索多个关键词组合"""
    query = " OR ".join(terms)
    mindate = f"{start_year}" if start_year else None
    maxdate = f"{end_year}" if end_year else None

    handle = Entrez.esearch(
        db="pubmed",
        term=query,
        retmax=max_results,
        api_key=API_KEY,
        datetype="pdat",   # 发表日期
        mindate=mindate,
        maxdate=maxdate,
    )
    print(f"搜索查询: {query}")
    record = Entrez.read(handle)
    handle.close()
    
    pmids = record["IdList"]
    print(f"找到 {len(pmids)} 篇文献")
    return pmids

def fetch_details(pmids ,API_KEY = None):
    """获取文献的详细信息"""
    ids = ",".join(pmids)
    handle = Entrez.efetch(db="pubmed", id=ids, retmode="xml", api_key=API_KEY)
    records = Entrez.read(handle)
    handle.close()
    
    articles = []
    for record in records["PubmedArticle"]:
        article = {}
        medline = record["MedlineCitation"]
        
        # 基本信息
        article["pmid"] = medline["PMID"]
        article["title"] = medline["Article"]["ArticleTitle"]
        
        # 作者列表
        authors = []
        if "AuthorList" in medline["Article"]:
            for author in medline["Article"]["AuthorList"]:
                try:
                    name = f"{author.get('LastName', '')}, {author.get('ForeName', '')}"
                    authors.append(name)
                except AttributeError:  # 有些作者可能是集体作者
                    authors.append(str(author.get("CollectiveName", "")))
        article["authors"] = authors
        
        # 期刊信息
        journal = medline["Article"]["Journal"]
        article["journal"] = journal["Title"]
        article["volume"] = journal.get("JournalIssue", {}).get("Volume", "")
        article["issue"] = journal.get("JournalIssue", {}).get("Issue", "")
        article["pages"] = medline["Article"].get("Pagination", {}).get("MedlinePgn", "")
        
        # 日期
        pub_date = journal["JournalIssue"]["PubDate"]
        article["year"] = pub_date.get("Year", "")
        article["month"] = pub_date.get("Month", "")
        article["day"] = pub_date.get("Day", "")
        
        # 摘要
        article["abstract"] = ""
        if "Abstract" in medline["Article"]:
            abstract_text = []
            for text in medline["Article"]["Abstract"]["AbstractText"]:
                if isinstance(text, str):
                    abstract_text.append(text)
                else:  # 有些摘要有标签
                    abstract_text.append(text.get("_", ""))
            article["abstract"] = " ".join(abstract_text)
        
        # DOI
        article["doi"] = ""
        for id in medline["Article"]["ELocationID"]:
            if id.attributes["EIdType"] == "doi":
                article["doi"] = str(id)
        
        articles.append(article)
    
    return articles

def by_doi_search(doi):
    try:
        url = f"https://doi.org/{quote(doi)}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        }
        session = requests.Session()
        response = session.get(url, headers=headers, allow_redirects=True, timeout=10)

        # 检查最终URL是否指向PDF
        if response.url.endswith(".pdf"):
            return response.url

        # 尝试在页面中查找PDF链接
        soup = BeautifulSoup(response.text, 'html.parser')
        pdf_links = []
        for link in soup.find_all('a'):
            href = link.get('href', '').lower()
            if href.endswith('.pdf') or 'pdf' in href or 'download' in href:
                pdf_links.append(link.get('href'))
        if pdf_links:
            return urljoin(response.url, pdf_links[0])
    except Exception as e:
        return None
        
def by_pmid_search(pmid):
    try:
        url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找PDF链接
        pdf_link = soup.find('a', {'class': 'id-link'})
        if pdf_link and 'href' in pdf_link.attrs:
            return urljoin(url, pdf_link['href'])
    except Exception as e:
        return None

def find_pdf_url(article):
    """尝试找到PDF下载链接"""
    pmid = article["pmid"]
    doi = article["doi"]
    try:
        # 首先尝试通过DOI获取PDF链接
        pdf_url = by_doi_search(doi)
        if pdf_url:
            return pdf_url
    except Exception as e:
        print(f"通过DOI获取PDF时出错: {str(e)}")
    try:
        # 如果DOI获取失败，尝试通过PMID获取PDF链接
        pdf_url = by_pmid_search(pmid)
        if pdf_url:
            return pdf_url
    except Exception as e:  
        print(f"通过PMID获取PDF时出错: {str(e)}")
    # 如果都失败了，记录错误
    with open(FAILED_DOWNLOADS, 'a', encoding='utf-8') as f:
        f.write(f"[PMID: {pmid}] [DOI: {doi}] - 无法获取PDF链接\n")
    return None

def download_pdf(url, pmid, title,doi=None):
    """下载PDF文件"""
    try:
        if not os.path.exists(PDF_DIR):
            os.makedirs(PDF_DIR)
        
        # 清理标题以用作文件名
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '.', '_')).rstrip()
        filename = f"{pmid}_{safe_title[:50]}.pdf"
        filepath = os.path.join(PDF_DIR, filename)
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers, stream=True, timeout=30)
        response.raise_for_status()
        final_url = response.url
        content_type = response.headers.get('Content-Type', '').lower()
        if ('pdf' not in content_type) and (not final_url.lower().endswith('.pdf')):
            raise ValueError(f"非PDF内容: {content_type} from {final_url}")
        # 获取文件总大小（可能不存在）
        file_size = int(response.headers.get('Content-Length', 0))
        # 进度条设置
        progress = tqdm(
            desc=f"Downloading {filepath}",
            total=file_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024
        )
        
        downloaded_bytes = 0
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(1024):
                if chunk:
                    f.write(chunk)
                    chunk_len = len(chunk)
                    downloaded_bytes += chunk_len
                    progress.update(chunk_len)
        progress.close()
        if file_size and downloaded_bytes < file_size:
            raise IOError(f"下载不完整: got {downloaded_bytes} of {file_size} bytes from {final_url}")
        return filepath
    except Exception as e:
        print(f"下载PDF时出错: {str(e)}")
        try:
            with open(FAILED_DOWNLOADS, 'a', encoding='utf-8') as f:
                f.write(f"[PMID: {pmid}] [DOI: {doi}] [URL: {url}] - 下载PDF时出错: {str(e)}\n")
                print(f"失败的链接已保存到：{FAILED_DOWNLOADS}")
        except Exception as e:
            print(f"保存失败记录时出错: {str(e)}")
        # 删除可能存在的空文件
        if os.path.exists(filepath):
            os.remove(filepath)
        return None

def main():
    # 搜索PubMed
    pmids = search_pubmed(SEARCH_TERMS, MAX_RESULTS)
    # 分批获取详细信息，避免请求过大
    batch_size = 10
    all_articles = []

    for i in tqdm(range(0, len(pmids), batch_size), desc="获取文献详情"):
        batch = pmids[i:i+batch_size]
        articles = fetch_details(batch)
        # 读取已有的JSON文件，如果不存在则创建
        try:
            with open(OUTPUT_JSON, 'r', encoding='utf-8') as f:
                all_articles = json.load(f)
        except FileNotFoundError:
            all_articles = []
        
        all_articles.extend(articles)
        
        # 更新
        with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
            json.dump(all_articles, f, indent=2, ensure_ascii=False)
        time.sleep(DELAY)
    
    print(f"文献元信息已保存到 {OUTPUT_JSON}")

    # 尝试下载PDF
    print("\n开始下载PDF...")
    downloaded = 0
    for article in tqdm(all_articles):
        pdf_url = find_pdf_url(article)
        if pdf_url:
            article["pdf_url"] = pdf_url
            result = download_pdf(pdf_url, article["pmid"], article["title"],article["doi"])
            if result:
                article["pdf_path"] = result
                downloaded += 1
            else:
                article["pdf_path"] = None
        else:
            article["pdf_url"] = None
            article["pdf_path"] = None
          
        time.sleep(DELAY)
    
    print(f"成功下载 {downloaded}/{len(all_articles)} 篇PDF")
    
    # 更新JSON文件包含PDF路径
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(all_articles, f, indent=2, ensure_ascii=False)
    print("更新后的文献信息已保存")

if __name__ == "__main__":
    main()