# BMJCaseReport

本目录包含用于批量抓取 BMJ Case Reports 论文链接及 PDF 文件的脚本。

## 目录结构

- `getLink.py`：抓取 BMJ Case Reports 论文的标题、链接和 PDF 下载地址，并保存为 Excel 文件。
- `getBMJCaseReports.py`：根据 Excel 文件中的链接批量下载论文 PDF，支持单线程和多线程下载。
- `data/`：存放已下载的 PDF 压缩包和下载失败的链接记录。
- `meta/`：元数据目录（可选）。

## 使用步骤

### Step 1: 获取论文链接

运行 [`getLink.py`](getLink.py) 脚本，抓取指定页码范围内的论文信息，并保存为 Excel 文件。


### Step 2: 批量下载PDF

运行 [`getBMJCaseReports.py`](getBMJCaseReports.py) 脚本，根据 Excel 文件中的链接批量下载 PDF 文件。

## 依赖环境
- Python 3.x
- requests
- pandas
- tqdm
- beautifulsoup4
