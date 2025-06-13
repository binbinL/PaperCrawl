from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
import pandas as pd
from tqdm import tqdm
import os
def get_html(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0',
        }
    response = requests.get(url,headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Failed to fetch page: {response.status_code}")

def get_paper_links(dst,begin_page,end_page):
    results = []
    for i in tqdm(range(begin_page,end_page)):
        url = "https://casereports.bmj.com/search/blood%20jcode%3Acasereports%7C%7Cbmjcr%20numresults%3A100%20sort%3Arelevance-rank"+'?page='+str(i)
        html = get_html(url)
        base_url = 'https://casereports.bmj.com/'
        soup = BeautifulSoup(html, 'html.parser')
        # 查找所有符合条件的a标签
        for a_tag in soup.find_all('a', class_='highwire-cite-linked-title'):
            # 提取href属性
            href = a_tag.get('href', '')
            if not href:
                continue
            absolute_url = urljoin(base_url, href)
            # 提取标题文本
            title_span = a_tag.find('span', class_='highwire-cite-title')
            title = title_span.get_text(strip=True) if title_span else '无标题'
            results.append({
                'title': title,
                'url': absolute_url,
                'relative_url': href,
                'pdf_link': absolute_url + '.full.pdf'
            })
    df = pd.DataFrame(results)
    print(len(df))
    df.to_excel(dst, index=False)

if __name__ == "__main__":
    dst = '/Users/binnn/workspace/BMJCaseReports/BMJCaseReports180-204.xlsx'
    begin_page = 180
    end_page = 204
    get_paper_links(dst,begin_page,end_page)