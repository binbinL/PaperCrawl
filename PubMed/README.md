# PubMed 抓取脚本说明

本目录包含 `Pubmed.py` 脚本，用于按关键词检索 PubMed 文章、保存元数据，并尝试抓取 PDF。

## 环境依赖
- Python 3.9+
- 包：`requests`, `beautifulsoup4`, `biopython`, `tqdm`
- 安装示例：
  ```bash
  pip install requests beautifulsoup4 biopython tqdm
  ```

## 运行前配置
在 `Pubmed.py` 顶部可按需调整：
- `Entrez.email`：必填，写自己的邮箱。
- `SEARCH_TERMS`：检索关键词列表，自动以 OR 组合。
- `MAX_RESULTS`：最大返回文献数。
- `SAVE_DIR`：数据输出目录（会写入 JSON、PDF、失败记录）。
- `DELAY`：请求间隔，保持符合 NCBI 频率限制。

## 使用方法
在本目录下运行：
```bash
python getPubmed.py
```
脚本流程：
1) 用 Entrez 搜索并拉取文章详情；
2) 追加/更新 `data/pubmed_results.json`；
3) 尝试解析 DOI 或 PMID 页找到 PDF 链接；
4) 下载 PDF 到 `data/pdfs/`，失败记录写入 `data/failed_downloads.txt`。

**注意**：若文献无在线pdf资源则无法正常下载，failed_download.txt中显示为“非PDF内容”

## 输出文件
- `data/pubmed_results.json`：文章元数据及下载结果。
- `data/pdfs/`：成功下载的 PDF。
- `data/failed_downloads.txt`：未找到或下载失败的链接日志。

## 常见问题
- **下载的文件打不开**：目标链接返回的可能是 HTML/登录页。脚本已增加 Content-Type 校验和不完整下载检查，失败会写入 `failed_downloads.txt`。可手动打开失败链接确认是否需登录或更换来源。
- **403/429 频率限制**：提高 `DELAY` 或减少 `MAX_RESULTS`，必要时添加 NCBI API key。
- **找不到 PDF**：部分期刊不提供开放 PDF，或 DOI 解析不到直链，可手动补充 `pdf_url` 再运行下载逻辑。
