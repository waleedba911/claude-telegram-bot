import os
import anthropic
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import base64

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY")

client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

SYSTEM_PROMPT = """أنت مساعد شخصي لوليد، Supply Chain Manager في شركة مطاعم بالسعودية.
مهامك:
- الإجابة على الأسئلة العامة بالعربية
- تحليل الفواتير وأوامر الشراء من الصور
- المساعدة في قرارات سلسلة الإمداد
أجب دائماً بالعربية بشكل مختصر ومفيد."""

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    
    try:
        if message.photo:
            photo = message.photo[-1]
            file = await context.bot.get_file(photo.file_id)
            file_bytes = await file.download_as_bytearray()
            image_data = base64.standard_b64encode(file_bytes).decode("utf-8")
            caption = message.caption or "حلل هذه الصورة"
            
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": image_data}},
                        {"type": "text", "text": caption}
                    ]
                }]
            )
        else:
            text = message.text or "مرحبا"
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": text}]
            )
        
        await message.reply_text(response.content[0].text)
    
    except Exception as e:
        await message.reply_text(f"حدث خطأ: {str(e)}")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
