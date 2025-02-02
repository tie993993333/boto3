# Telegram 商店及充值机器人

本项目是一个 Telegram 机器人，集成了商店、充值验证和多语言支持等功能。  
机器人主要功能包括：
- **用户注册**：用户发送 `/start` 命令后自动注册并分配专属充值地址。
- **余额查询**：通过 `/balance` 命令可查看当前余额（单位 USDT）。
- **充值验证**：
  - **手动验证**：用户使用 `/checkdeposit <交易ID>` 命令提交交易 ID，机器人调用 TRON API 验证充值。
  - **自动监控**：系统定时轮询预设的充值地址，检测新充值交易后自动更新对应用户余额，并发送通知。
- **商品浏览与下单**：通过 `/shop` 浏览商品分类，直接发送商品代码前6位购买（示例中每件商品固定 1 USDT）。
- **订单记录**：使用 `/orders` 命令查询用户订单记录（按下单时间倒序显示）。
- **多语言支持**：支持 CN、EN、JP、CA、FR 等语言；用户可以通过 `/setlang <语言代码>` 命令切换语言，所有提示信息会根据用户语言进行显示。
- **帮助信息**：通过 `/help` 命令查看所有可用命令及说明。
- **管理后台**：管理员可以使用 `/addprod <code> <category> <content>` 命令添加商品（需要管理员 Telegram 用户 ID）。

## 项目结构
下面提供一个详细的启动运行步骤说明，确保你能够顺利启动该项目：

安装 Python
确保你的系统上已安装 Python 3.7 或更高版本。

下载项目代码
将整个项目代码（包括 bot.py、database.py、config.py、requirements.txt 以及 README.md）下载到本地一个目录中，比如 tg_shop_bot/。

创建虚拟环境（可选，但推荐）
在项目根目录下打开终端（或命令提示符），执行以下命令：

Linux/Mac：
bash
複製
python3 -m venv venv
source venv/bin/activate
Windows：
bash
複製
python -m venv venv
venv\Scripts\activate
安装项目依赖
在虚拟环境中，执行以下命令安装依赖：

bash
複製
pip install -r requirements.txt
这将安装 python-telegram-bot 和 requests 库。

配置项目
打开 config.py 文件，按照你的实际情况填写：

Telegram 机器人的 TOKEN
管理员的 Telegram 用户 ID（ADMIN_IDS）
充值地址池（DEPOSIT_ADDRESSES，建议使用 TRON 地址的16进制格式）
TRON API 基础 URL（主网或测试网，例如主网为 https://api.trongrid.io）
API 金钥（API_KEY）
初始化数据库
第一次运行项目时，程序会自动在项目根目录下创建 SQLite 数据库文件（例如 shop.db），并创建用户、商品、订单和已处理交易记录等数据表。你无需手动执行其他操作。

启动机器人
在项目根目录下（确保虚拟环境已激活）运行：

bash
複製
python bot.py
运行后，终端会显示日志信息，表示机器人开始轮询并等待 Telegram 消息。

在 Telegram 上与机器人交互

打开 Telegram，搜索你的机器人（确保你使用的是在 config.py 中配置的 Token 对应的机器人）。
发送 /start 命令，机器人会自动注册你并分配专属充值地址，同时返回欢迎信息。
你可以依次使用 /balance、/shop、/setlang <语言代码>、/checkdeposit <交易ID>、/orders 和 /help 等命令来体验各项功能。
按照以上步骤，你就可以成功启动并运行该 Telegram 机器人项目。如果在运行过程中遇到任何问题，可以查看终端日志或阅读 README.md 文件中的使用说明进行排查。
