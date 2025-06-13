import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import pandas as pd
from tqdm import tqdm

def getPDF(dst,url_list):
    '''
    dst: 下载目录
    url_list: 需要下载的url列表
    该函数使用selenium模拟浏览器下载PDF文件
    '''
    for url in tqdm(url_list):
        options = webdriver.ChromeOptions()
        prefs = {
            'profile.default_content_settings.popups': 0,
            'download.default_directory': dst,  # 设置下载目录
            'download.directory_upgrade': True,
            'download.prompt_for_download': False,
            "safebrowsing.enabled": True
        }
        options.add_experimental_option('prefs', prefs)
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument("--disable-popup-blocking")
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        # 无头
        # options.add_argument('--headless')  # 设置为无头
        # options.add_argument('--disable-gpu')  # 设置没有使用gpu

        path = '/usr/local/bin/chromedriver'  # chromedriver的路径
        service = Service(executable_path=path)
        driver = webdriver.Chrome(service=service, options=options)
        try:
            # driver.get("https://onlinelibrary.wiley.com/doi/pdfdirect/10.1155/crh/7154679?download=true")
            driver.get(url)
            time.sleep(5)
        except Exception as e:
            print(f"Error occurred while processing {url}: {e}")
            continue  
        finally:
            driver.quit()
        
def readfile(file_path):
    df = pd.read_excel(file_path)
    urllist = df['download'].tolist()
    return urllist

if __name__ == "__main__":
    dst = '/Users/binnn/workspace/PaperCrawl/CaseReport/transplantation'
    filepath = '/Users/binnn/workspace/PaperCrawl/CaseReport/Case Reports in Transplantation_298.xlsx'
    urllist = readfile(filepath)
    getPDF(dst,urllist)

