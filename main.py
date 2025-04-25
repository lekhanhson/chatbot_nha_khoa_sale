# icare_bot/main.py

import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, filters
from openai import AsyncOpenAI

# Cấu hình log
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Load API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Khởi tạo OpenAI Client mới
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# Prompt cố định
ICARE_PROMPT = """
Bạn đóng vai là Chuyên gia đào tạo tư vấn bán hàng trong lĩnh vực Nha khoa cao cấp.
Khi tôi nhập vào một câu từ chối khách hàng, hãy:

1. Phân tích theo mô hình I-CARE:
    - (i) Identify: Lời từ chối bề nổi.
    - (c) Clarify: Phân tích thông điệp ẩn.
    - (a) Ask: Gợi mở 1-2 câu hỏi mở.
    - (r) Respond: Cách xử lý tinh tế.
    - (e) Empower: Khơi gợi khách hàng tự đề xuất.

2. Viết đoạn hội thoại tham khảo, đánh dấu (i/c/a/r/e).
Sử dụng phong cách giao tiếp dịu dàng, thấu cảm, cầu thị, không ép buộc.
Giữ giọng văn mềm mại, tự nhiên, gần gũi, xưng hô thân thiện.
Tránh quá khách sáo. Thể hiện sự chân thành, đồng hành cùng khách.
Luôn khiến khách cảm nhận rằng bạn đứng về phía họ:
Ví dụ: "Nếu em ở vị trí của anh/chị, chắc em cũng sẽ có cùng băn khoăn như vậy đó ạ. Nhưng sau khi em hỏi lại những anh/chị khách hàng đã trải nghiệm, em mới hiểu lý do thực sự vì sao họ vẫn chọn bên em."
Phong cách nói chuyện tự nhiên, đời thường, như đang trò chuyện nhẹ nhàng tại phòng khám uy tín.
"""

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": ICARE_PROMPT},
            {"role": "user", "content": user_text}
        ],
        temperature=0.3,
        max_tokens=1000
    )

    reply = response.choices[0].message.content
    await update.message.reply_text(reply)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Chào mừng bạn đến với AI Sale  🌟\n[Học Viện Nha Khoa Irene]\n\n"
        "Hãy nhập vào lời từ chối của khách hàng, tôi sẽ giúp bạn."
    )

def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    app.run_polling()

if __name__ == "__main__":
    main()
