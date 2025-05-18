# Bib-Zotero-to-Google

这个工具用于从Google Scholar爬取references.bib中的文献信息，并生成一个包含Google Scholar引用信息的新BibTeX文件（google.bib）。

## 功能

- 从已有的BibTeX文件（例如Zotero导出的文件）中提取文献标题
- 使用这些标题在Google Scholar上搜索对应的文献
- 获取Google Scholar中的文献信息，包括引用次数等
- 生成一个新的BibTeX文件，包含从Google Scholar获取的信息
- 支持代理设置，避免被Google Scholar封锁
- 自动轮换User-Agent，减少被检测的可能性
- 支持分批处理大量文献条目，避免长时间运行被中断
- 保存进度功能，可以从上次中断的地方继续处理
- 提供代理查找和测试工具，帮助避免IP被封
- 提供自动批处理工具，可以按批次处理大量文献

## 安装

1. 确保已安装Python 3.7+
2. 安装依赖包：

```bash
pip install -r requirements.txt
```

### Selenium和ChromeDriver安装

本脚本使用Selenium自动化浏览器操作，需要额外安装：

1. 安装Chrome浏览器（如果尚未安装）
   - 从[Chrome官网](https://www.google.com/chrome/)下载安装

2. ChromeDriver会通过webdriver-manager自动下载和管理，无需手动安装
   - webdriver-manager已包含在requirements.txt中
   - 如果自动下载失败，可以手动下载与您的Chrome版本匹配的ChromeDriver
   - 从[ChromeDriver官网](https://chromedriver.chromium.org/downloads)下载
   - 将下载的ChromeDriver放入系统PATH路径中

### 可能遇到的问题

1. 如果遇到"Chrome版本不匹配"错误，请确保您安装的Chrome版本与自动下载的ChromeDriver版本匹配
2. 在MacOS上，可能需要允许ChromeDriver运行：
   - 在系统偏好设置 -> 安全性与隐私 -> 通用 -> 允许应用
3. 在Linux上，可能需要安装额外的依赖：
   ```bash
   sudo apt-get install -y xvfb libxi6 libgconf-2-4
   ```
   
## 使用方法

### 基本用法

```bash
python google_scholar_scraper.py
```

这将读取当前目录下的`references.bib`文件，并生成`google.bib`文件。

### 高级选项

```bash
python google_scholar_scraper.py --input your_references.bib --output your_google.bib --delay 5
```

#### 参数说明

- `--input`: 输入的BibTeX文件路径（默认为 references.bib）
- `--output`: 输出的BibTeX文件路径（默认为 google.bib）
- `--delay`: 每次请求之间的延迟时间，单位为秒（默认为3秒，建议不要太小以避免被Google Scholar封禁）

### 使用代理

本脚本现在默认使用Selenium和Chrome浏览器来访问Google Scholar，并使用指定的代理：

```bash
python google_scholar_scraper.py
```

默认代理已设置为："http://user-usslab2013:db2013@pr.roxlabs.cn:4600"

如果你想使用其他代理，可以通过`--proxy`参数指定：

```bash
python google_scholar_scraper.py --proxy "http://your-proxy-username:password@host:port"
```

### 自动获取代理

本工具附带了一个代理查找和测试脚本，可以帮助你找到可用的免费代理：

```bash
python proxy_setup.py
```

该脚本会自动从免费代理网站获取代理列表，并测试它们的可用性，然后提供可直接复制粘贴的命令行参数。例如：

```
可用代理列表:
1. 103.152.112.162:80
2. 128.199.202.122:8080

使用示例:
python google_scholar_scraper.py --use-proxy --proxy-host 103.152.112.162 --proxy-port 80
```

你可以使用以下参数自定义代理查找过程：

```bash
python proxy_setup.py --max-test 50 --max-working 10
```

- `--max-test`: 最多测试多少个代理（默认20）
- `--max-working`: 找到多少个可用代理后停止（默认5）

### 自动批处理

对于大型BibTeX文件，我们提供了一个批处理脚本，可以自动将文件分成小批次处理，并在每批之间添加足够的延迟时间：

```bash
python batch_process.py
```

该脚本会自动计算文件中的条目数量，并按照指定的批次大小进行处理。默认情况下，每批处理5个条目，批次之间等待60秒。

你可以使用以下参数自定义批处理过程：

```bash
python batch_process.py --input references.bib --output google.bib --batch-size 10 --delay 120 --use-proxy --proxy-rotation
```

- `--input`: 输入文件路径（默认 references.bib）
- `--output`: 输出文件路径（默认 google.bib）
- `--batch-size`: 每批处理的条目数量（默认 5）
- `--delay`: 批次之间的等待时间，单位为秒（默认 60）
- `--use-proxy`: 启用代理（需要配合 --proxy-rotation 使用）
- `--proxy-rotation`: 为每个批次使用不同的代理（自动调用 proxy_setup.py）

使用批处理脚本的好处是它会自动处理所有的条目，并在每批之间添加足够的延迟时间，以减少被封禁的风险。同时，它还可以为每个批次自动查找新的代理。

### 分批处理文献

如果你想手动控制分批处理过程，可以使用以下命令：

```bash
# 处理前10篇文献
python google_scholar_scraper.py --start-index 0 --limit 10

# 处理接下来的10篇文献
python google_scholar_scraper.py --start-index 10 --limit 10
```

## 恢复进度

脚本会自动检查输出文件是否已存在，如果存在，会加载已有的条目并跳过已处理的条目。这样，如果脚本中途停止，你可以直接重新运行，它会从上次中断的地方继续。

## 注意事项

1. Google Scholar有严格的反爬虫机制，请合理设置延迟时间，避免IP被封
2. 建议使用`--delay`参数增加请求间隔（建议5-10秒）
3. 对于大量文献，强烈建议使用批处理脚本或`--start-index`和`--limit`参数分批处理
4. 如果遇到被封的情况，可以：
   - 等待一段时间后重试（至少几小时）
   - 使用代理服务
   - 更换网络环境
5. 免费代理通常不稳定，如果使用`proxy_setup.py`脚本找到的代理无效，请多尝试几个
6. 建议每次运行不超过20-30个条目，然后等待一段时间再继续

## 工作原理

1. 解析输入的BibTeX文件，提取每个条目的标题
2. 使用Selenium打开Chrome浏览器（无头模式）
3. 通过指定的代理连接到Google Scholar
4. 搜索文献标题
5. 点击"引用"按钮并获取BibTeX格式的引文
6. 将所有结果写入新的BibTeX文件

## 完整参数列表

```
usage: google_scholar_scraper.py [-h] [--input INPUT] [--output OUTPUT] [--delay DELAY] [--proxy PROXY]

Scrape Google Scholar for BibTeX references

optional arguments:
  -h, --help      显示帮助信息并退出
  --input INPUT   输入的BibTeX文件路径（默认为reference.bib）
  --output OUTPUT 输出的BibTeX文件路径（默认为google.bib）
  --delay DELAY   请求之间的延迟时间（秒）（默认为3秒）
  --proxy PROXY   代理URL（默认为http://user-usslab2013:db2013@pr.roxlabs.cn:4600）