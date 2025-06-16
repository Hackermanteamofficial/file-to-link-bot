import telebot
import requests
import os

# توکن رباتت رو اینجا بگذار
API_TOKEN = 'YOUR_BOT_TOKEN'
bot = telebot.TeleBot(API_TOKEN)

# محدودیت حجم به بایت (2 گیگابایت = 2 * 1024 * 1024 * 1024)
MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024

@bot.message_handler(content_types=['document', 'video', 'audio'])
def handle_file(message):
    file_id = message.document.file_id
    file_name = message.document.file_name
    file_size = message.document.file_size

    # بررسی محدودیت حجم
    if file_size > MAX_FILE_SIZE:
        bot.reply_to(message, "❌ فایل بیشتر از ۲ گیگابایت است. لطفاً فایل کوچکتری بفرست.")
        return

    msg = bot.reply_to(message, "⏳ در حال پردازش فایل...")

    # دریافت لینک فایل از سرور تلگرام
    file_info = bot.get_file(file_id)
    file_url = f"https://api.telegram.org/file/bot{API_TOKEN}/{file_info.file_path}"
    file_data = requests.get(file_url).content

    # ذخیره فایل موقتاً
    with open(file_name, 'wb') as f:
        f.write(file_data)

    # آپلود به gofile.io
    with open(file_name, 'rb') as f:
        upload_url = 'https://api.gofile.io/uploadFile'
        res = requests.post(upload_url, files={'file': f})
        data = res.json()

    # بررسی نتیجه
    if data['status'] == 'ok':
        download_link = data['data']['downloadPage']
        bot.edit_message_text(f"✅ فایل با موفقیت آپلود شد!\n🔗 لینک دانلود:\n{download_link}", chat_id=msg.chat.id, message_id=msg.message_id)
    else:
        bot.edit_message_text("❌ خطا در آپلود فایل!", chat_id=msg.chat.id, message_id=msg.message_id)

    # حذف فایل موقتی
    os.remove(file_name)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "سلام! 👋\nفایل خود را ارسال کنید تا لینک دانلود دریافت کنید. حداکثر حجم: ۲ گیگابایت.")

bot.polling(non_stop=True)