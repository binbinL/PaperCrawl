# CaseReport

本目录包含用于批量下载 Case Reports in xxx 论文 PDF 的脚本。

## 目录结构

- `getCaseReports.py`：主脚本，读取 Excel 文件中的下载链接，使用 Selenium 自动化浏览器批量下载 PDF。
- `data/`：可选，存放已下载的 PDF 文件或下载记录。
- `meta/`：如 `Case Reports in Transplantation_298.xlsx`，包含论文的下载链接。

## 使用步骤

### Step 1: 获取论文链接

首先将对应页面的html下载至本地，运行 [`getLink.py`](getLink.py) 脚本，通过正则获取论文链接。


### Step 2: 批量下载PDF

运行 [`getCaseReports.py`](getCaseReports.py) 脚本，根据 Excel 文件中的链接，使用 Selenium 控制 Chrome 浏览器批量下载 PDF 文件到指定目录。


## 依赖环境

- Python 3.x
- selenium
- pandas
- tqdm
- Chrome 浏览器
- ChromeDriver（需与 Chrome 版本匹配）
