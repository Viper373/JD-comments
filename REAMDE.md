# 🛒京东商品评论爬虫

这个项目是一个用于爬取京东商品评论的Python脚本。它可以帮助用户获取指定商品的评论数据，并将数据存储在CSV文件中。

## 💄功能特点

- 爬取指定商品的评论数据。
- 将评论数据存储在CSV文件中，方便后续分析和处理。
- 由于京东单个商品评论数量只显示990条（日期区分），因此该项目每天爬取一次，可将项目部署在服务器上，每天定时执行。

## 💎依赖
   * 项目版本：`Python 3.10.7`

## 💍安装

### 🎐 1. 克隆这个仓库到本地：

```bash
git clone https://github.com/Viper373/JD_comments
git clone git@github.com:Viper373/JD_comments.git # 若网络无法访问，请使用ssh方式
```

### 🎑 2. 进入项目目录：

```bash
cd JD_comments
```

### 🎀 3. 安装依赖：

```bash
pip install -r requirements.txt
```

## 🎨使用方法

🎈1. 配置`config.py`文件中的商品信息和数据存储路径。

🎈2. 运行`main.py`文件：

```bash
python main.py
```

## 🎉注意事项

- 🎗请确保你的网络环境能够访问京东网站。
- 🎗请根据京东的反爬虫策略合理设置爬取频率，避免被封IP或其他限制。

## 🧨示例

简单的`config.py`配置示例：在`PRODUCTS`中添加需要爬取的商品信息，包括商品ID、类型和名称。在`DATA_PATH`中设置数据存储路径。
