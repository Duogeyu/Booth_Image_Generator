# Booth Image Generator

Booth Image Generator是一个用于从Booth平台获取最新VRChat商品信息并生成商品预览图的Python脚本。

## 功能

- **获取最新商品信息**：从Booth平台获取最新的VRChat商品。
- **生成商品预览图**：根据商品信息生成带有二维码和色彩分析的预览图。

## 安装

1. 克隆此仓库：

   ```bash
   git clone https://github.com/yourusername/booth-image-generator.git
   ```

2. 进入项目目录：

   ```bash
   cd booth-image-generator
   ```

3. 安装依赖：

   ```bash
   pip install -r requirements.txt
   ```

## 使用方法

### 获取最新商品信息

使用以下命令获取最新的VRChat商品信息并更新本地数据文件：

```bash
python booth_image.py fetch
```

### 生成商品预览图

使用以下命令生成指定商品ID的预览图：

```bash
python booth_image.py generate <item_id>
```

生成的图片将保存在`data/`目录下。

## 配置

- **代理设置**：脚本默认使用`127.0.0.1:7890`作为HTTP代理。如果需要更改，请修改脚本中的`PROXY`变量。
- **User-Agent**：可以根据需要更改`HEADERS`中的User-Agent字符串。

## 依赖

- Python 3.x
- requests
- BeautifulSoup4
- selenium
- Pillow
- qrcode

## 注意事项

- 确保在运行脚本之前已正确配置Selenium的WebDriver。
- 本项目仅用于学习和个人使用，请遵守Booth平台的使用条款。

## 贡献

欢迎贡献代码和建议！请通过提交issue或pull request参与项目。

## 许可证

本项目采用AGPL-3.0许可证。

---

