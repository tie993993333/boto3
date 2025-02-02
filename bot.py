# bot.py
import logging
import requests
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Updater, CommandHandler, CallbackQueryHandler,
    CallbackContext, MessageHandler, Filters
)
import database
from config import TOKEN, ADMIN_IDS, DEPOSIT_ADDRESSES, TRON_API_BASE, API_KEY

# 初始化日志
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 全局翻译字典（支持 CN、EN、JP、CA、FR）
translations = {
    "welcome": {
        "CN": "欢迎 {name}！\n您的专属充值地址为：{address}\n使用 /balance 查询余额，\n使用 /checkdeposit <交易ID> 手动验证充值，\n使用 /shop 浏览商品。\n购买时可直接发送商品代码前6位，如：123456",
        "EN": "Welcome {name}!\nYour deposit address is: {address}\nUse /balance to check your balance,\nUse /checkdeposit <txid> to manually verify a deposit,\nUse /shop to browse products.\nTo purchase, send the first 6 digits of the product code, e.g., 123456",
        "JP": "ようこそ {name} さん！\nあなたの専用入金アドレスは：{address}\n/ balance で残高を確認してください。\n/checkdeposit <取引ID> で入金を手動で確認できます。\n/shop で商品を閲覧できます。\n購入するには、商品コードの最初の6桁を送信してください。例：123456",
        "CA": "Bienvenue {name}!\nVotre adresse de dépôt est : {address}\nUtilisez /balance pour vérifier votre solde,\nUtilisez /checkdeposit <txid> pour vérifier un dépôt manuellement,\nUtilisez /shop pour parcourir les produits.\nPour acheter, envoyez les 6 premiers chiffres du code produit, par exemple : 123456",
        "FR": "Bienvenue {name}!\nVotre adresse de dépôt est : {address}\nUtilisez /balance pour vérifier votre solde,\nUtilisez /checkdeposit <txid> pour vérifier un dépôt manuellement,\nUtilisez /shop pour parcourir les produits.\nPour acheter, envoyez les 6 premiers chiffres du code produit, ex. : 123456"
    },
    "balance": {
        "CN": "您的余额：{balance} USDT",
        "EN": "Your balance is: {balance} USDT",
        "JP": "あなたの残高は {balance} USDT です",
        "CA": "Votre solde est : {balance} USDT",
        "FR": "Votre solde est : {balance} USDT"
    },
    "setlang_success": {
        "CN": "语言已更改为 {lang}",
        "EN": "Language has been changed to {lang}",
        "JP": "{lang} に言語が変更されました",
        "CA": "La langue a été changée en {lang}",
        "FR": "La langue a été changée en {lang}"
    },
    "unknown_lang": {
        "CN": "未知语言代码。支持：CN, EN, JP, CA, FR",
        "EN": "Unknown language code. Supported: CN, EN, JP, CA, FR",
        "JP": "不明な言語コードです。サポートされている言語: CN, EN, JP, CA, FR",
        "CA": "Code de langue inconnu. Pris en charge : CN, EN, JP, CA, FR",
        "FR": "Code de langue inconnu. Pris en charge : CN, EN, JP, CA, FR"
    },
    "setlang_usage": {
        "CN": "用法：/setlang <语言代码>\n支持：CN, EN, JP, CA, FR",
        "EN": "Usage: /setlang <language code>\nSupported: CN, EN, JP, CA, FR",
        "JP": "使い方：/setlang <言語コード>\nサポート：CN, EN, JP, CA, FR",
        "CA": "Usage : /setlang <code de langue>\nPris en charge : CN, EN, JP, CA, FR",
        "FR": "Usage : /setlang <code de langue>\nPris en charge : CN, EN, JP, CA, FR"
    },
    "checkdeposit_usage": {
        "CN": "用法：/checkdeposit <交易ID>",
        "EN": "Usage: /checkdeposit <txid>",
        "JP": "使い方：/checkdeposit <取引ID>",
        "CA": "Usage : /checkdeposit <txid>",
        "FR": "Usage : /checkdeposit <txid>"
    },
    "deposit_success": {
        "CN": "充值成功！充值金额：{amount} USDT\n您的新余额：{new_balance} USDT",
        "EN": "Deposit successful! Amount: {amount} USDT\nYour new balance is: {new_balance} USDT",
        "JP": "入金成功！入金額：{amount} USDT\n新しい残高：{new_balance} USDT",
        "CA": "Dépôt réussi ! Montant : {amount} USDT\nVotre nouveau solde est : {new_balance} USDT",
        "FR": "Dépôt réussi ! Montant : {amount} USDT\nVotre nouveau solde est : {new_balance} USDT"
    },
    "deposit_failed": {
        "CN": "充值验证失败：{error}",
        "EN": "Deposit verification failed: {error}",
        "JP": "入金確認に失敗しました：{error}",
        "CA": "Échec de la vérification du dépôt : {error}",
        "FR": "Échec de la vérification du dépôt : {error}"
    },
    "order_success": {
        "CN": "购买成功！\n商品内容：{content}\n剩余余额：{new_balance} USDT",
        "EN": "Purchase successful!\nProduct: {content}\nRemaining balance: {new_balance} USDT",
        "JP": "購入成功！\n商品内容：{content}\n残りの残高：{new_balance} USDT",
        "CA": "Achat réussi !\nProduit : {content}\nSolde restant : {new_balance} USDT",
        "FR": "Achat réussi !\nProduit : {content}\nSolde restant : {new_balance} USDT"
    },
    "insufficient_balance": {
        "CN": "余额不足，请先充值。",
        "EN": "Insufficient balance, please deposit first.",
        "JP": "残高不足です。先に入金してください。",
        "CA": "Solde insuffisant, veuillez déposer d'abord.",
        "FR": "Solde insuffisant, veuillez déposer d'abord."
    },
    "invalid_product": {
        "CN": "未找到对应商品，请检查代码是否正确。",
        "EN": "No matching product found. Please check the code.",
        "JP": "該当する商品が見つかりません。コードを確認してください。",
        "CA": "Aucun produit correspondant trouvé. Veuillez vérifier le code.",
        "FR": "Aucun produit correspondant trouvé. Veuillez vérifier le code."
    },
    "shop_prompt": {
        "CN": "请选择商品分类：",
        "EN": "Please choose a product category:",
        "JP": "商品カテゴリーを選んでください：",
        "CA": "Veuillez choisir une catégorie de produit :",
        "FR": "Veuillez choisir une catégorie de produit :"
    },
    "orders_empty": {
        "CN": "您还没有订单记录。",
        "EN": "You have no order history.",
        "JP": "注文履歴はありません。",
        "CA": "Vous n'avez aucun historique de commande.",
        "FR": "Vous n'avez aucun historique de commande."
    },
    "orders_list": {
        "CN": "您的订单记录：\n{orders}",
        "EN": "Your order history:\n{orders}",
        "JP": "あなたの注文履歴：\n{orders}",
        "CA": "Votre historique de commande :\n{orders}",
        "FR": "Votre historique de commande :\n{orders}"
    },
    "help_message": {
        "CN": ("可用命令：\n"
               "/start - 注册并获取充值地址\n"
               "/balance - 查询余额\n"
               "/checkdeposit <交易ID> - 手动验证充值\n"
               "/shop - 浏览商品\n"
               "/setlang <语言代码> - 切换语言 (CN, EN, JP, CA, FR)\n"
               "/orders - 查看订单记录\n"
               "/help - 查看帮助信息"),
        "EN": ("Available commands:\n"
               "/start - Register and get deposit address\n"
               "/balance - Check balance\n"
               "/checkdeposit <txid> - Manually verify a deposit\n"
               "/shop - Browse products\n"
               "/setlang <lang> - Change language (CN, EN, JP, CA, FR)\n"
               "/orders - View order history\n"
               "/help - Show this help message"),
        "JP": ("利用可能なコマンド：\n"
               "/start - 登録して入金アドレスを取得\n"
               "/balance - 残高を確認\n"
               "/checkdeposit <取引ID> - 入金を手動で確認\n"
               "/shop - 商品を閲覧\n"
               "/setlang <言語コード> - 言語を変更 (CN, EN, JP, CA, FR)\n"
               "/orders - 注文履歴を確認\n"
               "/help - ヘルプを表示"),
        "CA": ("Commandes disponibles :\n"
               "/start - Inscription et obtention de l'adresse de dépôt\n"
               "/balance - Vérifier le solde\n"
               "/checkdeposit <txid> - Vérifier manuellement un dépôt\n"
               "/shop - Parcourir les produits\n"
               "/setlang <lang> - Changer la langue (CN, EN, JP, CA, FR)\n"
               "/orders - Voir l'historique des commandes\n"
               "/help - Afficher ce message d'aide"),
        "FR": ("Commandes disponibles :\n"
               "/start - Inscription et obtention de l'adresse de dépôt\n"
               "/balance - Vérifier le solde\n"
               "/checkdeposit <txid> - Vérifier manuellement un dépôt\n"
               "/shop - Parcourir les produits\n"
               "/setlang <lang> - Changer la langue (CN, EN, JP, CA, FR)\n"
               "/orders - Voir l'historique des commandes\n"
               "/help - Afficher ce message d'aide")
    }
}

# 辅助函数：根据 key 与用户语言返回翻译后的文本
def translate(key, lang, **kwargs):
    text = translations.get(key, {}).get(lang, translations.get(key, {}).get("EN", ""))
    return text.format(**kwargs)

# /setlang 命令：切换用户语言
def setlang(update: Update, context: CallbackContext):
    user = update.effective_user
    try:
        lang = context.args[0].upper()  # 如 EN, CN, JP, CA, FR
    except IndexError:
        update.message.reply_text(translate("setlang_usage", "EN"))
        return
    if lang not in ["CN", "EN", "JP", "CA", "FR"]:
        update.message.reply_text(translate("unknown_lang", "EN"))
        return
    database.set_user_language(user.id, lang)
    update.message.reply_text(translate("setlang_success", lang, lang=lang))

# /start 命令：注册用户、分配充值地址，并显示欢迎信息（使用用户语言）
def start(update: Update, context: CallbackContext):
    user = update.effective_user
    database.add_user(user.id, user.username or user.first_name)
    lang = database.get_user_language(user.id)
    user_address = database.get_user_deposit_address(user.id)
    if not user_address:
        assigned = database.get_all_assigned_deposit_addresses()
        for addr in DEPOSIT_ADDRESSES:
            if addr not in assigned:
                database.assign_deposit_address_to_user(user.id, addr)
                user_address = addr
                break
    update.message.reply_text(translate("welcome", lang, name=user.first_name, address=user_address))

# 查询余额
def balance(update: Update, context: CallbackContext):
    user = update.effective_user
    lang = database.get_user_language(user.id)
    bal = database.get_user_balance(user.id)
    update.message.reply_text(translate("balance", lang, balance=bal))

# 手动验证充值：/checkdeposit <交易ID>
def check_deposit(update: Update, context: CallbackContext):
    try:
        txid = context.args[0]
    except IndexError:
        update.message.reply_text(translate("checkdeposit_usage", database.get_user_language(update.effective_user.id)))
        return
    valid, result = verify_deposit_tx(txid, DEPOSIT_ADDRESSES)
    lang = database.get_user_language(update.effective_user.id)
    if not valid:
        update.message.reply_text(translate("deposit_failed", lang, error=result))
        return
    amount = result
    user = update.effective_user
    current = database.get_user_balance(user.id)
    new_bal = current + amount
    database.update_user_balance(user.id, new_bal)
    update.message.reply_text(translate("deposit_success", lang, amount=amount, new_balance=new_bal))

# 使用 Trongrid API 验证单笔交易是否为有效充值
def verify_deposit_tx(txid, deposit_addresses):
    url = f"{TRON_API_BASE}/wallet/gettransactioninfobyid"
    data = {"value": txid}
    try:
        response = requests.post(url, json=data, timeout=10)
        response.raise_for_status()
        tx_info = response.json()
        if tx_info.get('contractRet') != 'SUCCESS':
            return False, "交易未成功"
        logs = tx_info.get('log', [])
        for log in logs:
            topics = log.get('topics', [])
            if any(addr.lower() in topic.lower() for addr in deposit_addresses for topic in topics):
                hex_amount = log.get('data')
                if hex_amount:
                    if hex_amount.startswith("0x"):
                        hex_amount = hex_amount[2:]
                    try:
                        amount_int = int(hex_amount, 16)
                        amount = amount_int / 1e6
                        return True, amount
                    except Exception as e:
                        return False, f"金额解析失败: {e}"
        return False, "未找到包含收款地址的交易记录"
    except Exception as e:
        return False, str(e)

# 商品浏览：展示分类
def shop(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("分类 A", callback_data='cat_A')],
        [InlineKeyboardButton("分类 B", callback_data='cat_B')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(translate("shop_prompt", database.get_user_language(update.effective_user.id)), reply_markup=reply_markup)

# 回调函数处理商品分类选择
def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    data = query.data
    if data.startswith('cat_'):
        category = data.split('_')[1]
        products = database.get_products_by_category(category)
        if products:
            text = f"分类 {category} 商品列表：\n"
            for prod in products:
                text += f"代码：{prod['code']}  内容：{prod['content']}\n"
        else:
            text = "该分类暂无商品。"
        query.edit_message_text(text=text)

# 通过用户发送前6位代码购买商品（每件商品价格固定为 1 USDT）
def buy_by_code(update: Update, context: CallbackContext):
    text = update.message.text.strip()
    if len(text) < 6:
        update.message.reply_text("请输入至少6位的商品代码前缀")
        return
    prefix = text[:6]
    product = database.get_product_by_code_prefix(prefix)
    if not product:
        update.message.reply_text(translate("invalid_product", database.get_user_language(update.effective_user.id)))
        return
    price = 1.0
    user = update.effective_user
    current = database.get_user_balance(user.id)
    if current < price:
        update.message.reply_text(translate("insufficient_balance", database.get_user_language(user.id)))
        return
    database.update_user_balance(user.id, current - price)
    database.create_order(user.id, product["id"])
    update.message.reply_text(translate("order_success", database.get_user_language(user.id), content=product["content"], new_balance=current - price))

# 管理后台：添加商品（仅限管理员）
def admin_add_product(update: Update, context: CallbackContext):
    user = update.effective_user
    if user.id not in ADMIN_IDS:
        update.message.reply_text("您无权限使用此命令。")
        return
    try:
        code = context.args[0]
        category = context.args[1]
        content = " ".join(context.args[2:])
    except IndexError:
        update.message.reply_text("用法：/addprod <code> <category> <content>")
        return
    database.add_product(code, category, content)
    update.message.reply_text(f"添加商品成功：代码 {code}，分类 {category}")

# /orders 命令：查看订单记录
def orders(update: Update, context: CallbackContext):
    user = update.effective_user
    lang = database.get_user_language(user.id)
    order_rows = database.get_orders(user.id)
    if not order_rows:
        update.message.reply_text(translate("orders_empty", lang))
    else:
        orders_str = ""
        for order in order_rows:
            orders_str += f"订单ID: {order['id']}, 商品ID: {order['product_id']}, 时间: {order['order_time']}, 状态: {order['status']}\n"
        update.message.reply_text(translate("orders_list", lang, orders=orders_str))

# /help 命令：显示帮助信息
def help_command(update: Update, context: CallbackContext):
    user = update.effective_user
    lang = database.get_user_language(user.id)
    update.message.reply_text(translate("help_message", lang))

# 定时任务：轮询每个已分配充值地址的新交易，并自动更新对应用户余额
def poll_deposits(context: CallbackContext):
    headers = {"TRON-PRO-API-KEY": API_KEY}
    for address in DEPOSIT_ADDRESSES:
        user = database.get_user_by_deposit_address(address)
        if not user:
            continue
        url = f"{TRON_API_BASE}/v1/accounts/{address}/transactions/trc20"
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            transactions = data.get("data", [])
            for tx in transactions:
                txid = tx.get("transaction_id")
                if not txid:
                    continue
                if database.is_tx_processed(txid):
                    continue
                if tx.get("to", "").lower() != address.lower():
                    continue
                try:
                    value_hex = tx.get("value", "")
                    if value_hex.startswith("0x"):
                        value_hex = value_hex[2:]
                    amount_int = int(value_hex, 16)
                    amount = amount_int / 1e6
                except Exception as e:
                    logger.error(f"解析交易金额失败：{e}")
                    continue
                database.add_processed_tx(txid)
                current = database.get_user_balance(user["user_id"])
                new_bal = current + amount
                database.update_user_balance(user["user_id"], new_bal)
                context.bot.send_message(
                    chat_id=user["user_id"],
                    text=f"检测到新充值：{amount} USDT\n交易ID：{txid}\n您的新余额：{new_bal} USDT"
                )
        except Exception as e:
            logger.error(f"轮询地址 {address} 交易时出错：{e}")

def main():
    database.init_db()
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("balance", balance))
    dp.add_handler(CommandHandler("checkdeposit", check_deposit))
    dp.add_handler(CommandHandler("shop", shop))
    dp.add_handler(CommandHandler("addprod", admin_add_product))
    dp.add_handler(CommandHandler("setlang", setlang))
    dp.add_handler(CommandHandler("orders", orders))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, buy_by_code))

    job_queue = updater.job_queue
    job_queue.run_repeating(poll_deposits, interval=60, first=10)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
