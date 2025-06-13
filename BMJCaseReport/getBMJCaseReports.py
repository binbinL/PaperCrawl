from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
import pandas as pd
from tqdm import tqdm
import os

def download_pdf(url, save_path, headers=None, timeout=10):
    try:
        # 设置默认请求头
        headers = headers or {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
        }
        # 发起带流式传输的GET请求
        response = requests.get(url, headers=headers, stream=True, timeout=timeout)
        response.raise_for_status()  # 检查HTTP状态码
        content_type = response.headers.get('Content-Type', '')
        if 'application/pdf' not in content_type:
            raise ValueError(f"非PDF内容类型: {content_type}")
        # 确保保存目录存在
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        # 获取文件总大小（可能不存在）
        file_size = int(response.headers.get('Content-Length', 0))
        # 进度条设置
        progress = tqdm(
            desc=f"Downloading {os.path.basename(save_path)}",
            total=file_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024
        )

        # 写入文件
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:  # 过滤保持连接的空白块
                    f.write(chunk)
                    progress.update(len(chunk))
        progress.close()
        return True

    except Exception as e:
        print(f"下载失败: {url}")
        print(f"错误信息: {str(e)}")
        # 删除可能存在的空文件
        if os.path.exists(save_path):
            os.remove(save_path)
        return False


def batch_download(title_list, url_list, save_dir, failed_pth,headers=None):
    '''
    单线程下载
    '''
    print(f"开始批量下载，共{len(url_list)}个文件...")
    success_count = 0
    failed_urls = []

    for index, url in enumerate(url_list):
        file_name = title_list[index]+'.pdf'
        
        save_path = os.path.join(save_dir, file_name)
        
        print(f"\n正在下载第{index}/{len(url_list)}个文件: {file_name}")
        if download_pdf(url, save_path, headers):
            success_count += 1
        else:
            failed_urls.append(url)

    # 输出统计信息
    print(f"\n下载完成 成功: {success_count}个，失败: {len(failed_urls)}个")
    if failed_urls:
        failed_file = os.path.join(save_dir, failed_pth)
        try:
            with open(failed_file, 'a', encoding='utf-8') as f:
                f.write('\n')
                f.write('\n'.join(failed_urls))
            print(f"失败的链接已保存到：{failed_file}")
        except Exception as e:
            print(f"保存失败记录时出错: {str(e)}")
            print("以下是失败的链接：")
            print('\n'.join(failed_urls))

import concurrent.futures

def batch_download_Mthread(title_list, url_list, save_dir,failed_pth, headers=None, max_workers=8):
    print(f"开始批量下载，共{len(url_list)}个文件...")
    success_count = 0
    failed_urls = []

    def download_task(index):
        file_name = title_list[index] + '.pdf'
        save_path = os.path.join(save_dir, file_name)
        print(f"\n正在下载第{index}/{len(url_list)}个文件: {file_name}")
        if download_pdf(url_list[index], save_path, headers):
            return True, None
        else:
            return False, url_list[index]

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(download_task, idx): idx for idx in range(len(url_list))}
        for future in concurrent.futures.as_completed(futures):
            ok, fail_url = future.result()
            if ok:
                success_count += 1
            elif fail_url:
                failed_urls.append(fail_url)

    # 输出统计信息
    print(f"\n下载完成 成功: {success_count}个，失败: {len(failed_urls)}个")
    if failed_urls:
        try:
            with open(failed_pth, 'a', encoding='utf-8') as f:
                f.write('\n')
                f.write('\n'.join(failed_urls))
            print(f"失败的链接已保存到：{failed_pth}")
        except Exception as e:
            print(f"保存失败记录时出错: {str(e)}")
            print("以下是失败的链接：")
            print('\n'.join(failed_urls))


if __name__ == "__main__":
    df = pd.read_excel('/Users/binnn/workspace/BMJCaseReports/BMJCaseReports180-204.xlsx')
    title_list = df['url'].apply(lambda x: x.split('/')[-1]).tolist() 
    url_list = df['pdf_link'].tolist()
    save_dir='/Users/binnn/workspace/BMJCaseReport/18000-'
    failed_pth ='/Users/binnn/workspace/BMJCaseReport/failed_downloads(18000-).txt'
    batch_download_Mthread(title_list, url_list, save_dir=save_dir,failed_pth =failed_pth )
