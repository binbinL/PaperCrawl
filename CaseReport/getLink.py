from bs4 import BeautifulSoup
import re
import pandas as pd

def main():
    '''
    1.把网站html下载到本地
    2.使用正则表达式提取PDF链接和名称
    3.保存到Excel文件
    '''
    with open("/Users/binnn/Code/BGI/data/Case Reports in Transplantation Articles.html", "r", encoding="utf-8") as f:
        html_content = f.read()

    pattern = r'PdfLink</span>"&gt;</span><span class="html-tag">&lt;a <span class="html-attribute-name">title</span>="<span class="html-attribute-value">EPDF</span>" <span class="html-attribute-name">href</span>="<a class="html-attribute-value html-external-link" target="_blank" href="(.*?)" rel="noreferrer noopener">(.*?)</a>" <span class="html-attribute-name">aria-label</span>="<span class="html-attribute-value">(.*?)</span>"'
    res = re.findall(pattern, html_content, re.DOTALL | re.IGNORECASE)  
    data = []
    for item in res:
        pdflink = item[1]
        download = pdflink.replace('epdf','pdfdirect')+ '?download=true'
        name = item[2][9:]  
        data.append({"pdflink": pdflink, "name": name, "download": download})

    df = pd.DataFrame(data)
    print(df)
    df.to_excel("/Users/binnn/workspace/PaperCrawl/CaseReport/meta/Case Reports in Transplantation_298.xlsx", index=False)

if __name__ == "__main__":
    main()