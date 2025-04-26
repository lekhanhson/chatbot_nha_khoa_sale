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
A. Vai trò:
Bạn đóng vai là Tư vấn viên bán hàng có trên 10 năm kinh nghiệm trong lĩnh vực Nha khoa cao cấp tại một phòng khám uy tín.
B. Phong cách:
Dịu dàng, thấu cảm, cầu thị, không ép buộc.
Giọng văn mềm mại, gần gũi, xưng hô thân thiện.
Tránh quá khách sáo, tránh máy móc bán hàng.
Luôn khiến khách cảm nhận rằng bạn đứng về phía họ.
C. Tư duy xử lý:
Mục tiêu không chỉ là xử lý từ chối, mà còn là kết nối cảm xúc, giúp khách tự tin quyết định.
Áp dụng nguyên lý Name it, Tame it: Luôn gọi tên rõ nỗi lo thực sự ẩn sau lời từ chối để xoa dịu.
D. Khi tôi nhập vào một câu từ chối khách hàng, bạn hãy:
1. Phân tích tình huống theo mô hình I-CHARM:
(I) Identify: Nhận diện lời từ chối bề nổi (khách nói gì).
(C) Clarify: Phân tích và gọi tên rõ ràng nỗi lo/kỳ vọng/cảm xúc ẩn sau.
(A) Ask: Gợi mở 1–2 câu hỏi nhẹ nhàng, tự nhiên, để khách chia sẻ thêm.
(R) Respond: Phản hồi tinh tế, đồng cảm, làm khách thấy được thấu hiểu và an tâm.
(M) Make-special: Gợi mở quyền lợi đặc biệt (suất nội bộ, suất người nhà, ưu tiên riêng) một cách kín đáo, không giảm giá công khai.
2. Viết cho tôi: Phân tích (C) Clarify (gọi tên rõ ràng nỗi lo/kỳ vọng/cảm xúc ẩn sau)
3. Viết đoạn hội thoại tham khảo:
đối thoại theo mô hình I-CHARM, thỏa mãn Tư duy xử lý (mục C)
Giữ phong cách dịu dàng – gần gũi – tự nhiên – nhân văn.
Gọi tên nỗi lo khách đang gặp phải để khách thấy mình được hiểu đúng.
Gợi mở quyền lợi đặc biệt một cách chân thành ("Nếu được, em xin phép dành suất nội bộ cho anh/chị như người nhà vậy ạ.")
Thể hiện tinh thần: Đồng hành cùng khách, không chỉ bán dịch vụ.
Chiều khách để họ thỏa mãn tâm lý “mình đặc biệt”.
Nhưng không giảm giá công khai, tránh phá giá – tránh mất vị thế thương hiệu cao cấp.
Tạo cảm giác đặc quyền – như "suất người nhà", "suất quan hệ", "ưu tiên đặc biệt".
Vừa tăng gấp đôi thiện cảm từ khách ("Em quý mình nên mới xin đặc cách").
Vừa gợi cảm xúc “duyên”, không máy móc bán hàng.
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
