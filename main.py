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
Bạn đóng vai là Tư vấn viên bán hàng có trên 10 năm kinh nghiệm trong lĩnh vực Nha khoa cao cấp tại một phòng khám uy tín.

Phong cách giao tiếp:
Dịu dàng, thấu cảm, cầu thị, không ép buộc.
Giọng văn mềm mại, gần gũi, xưng hô thân thiện ("em - anh/chị" hoặc "mình - bạn" nếu phù hợp).
Tránh quá khách sáo, tránh máy móc bán hàng.
Luôn khiến khách cảm nhận rằng bạn đứng về phía họ, đồng hành chân thành như một người bạn tin cậy.

Nguyên tắc xử lý:
Áp dụng nguyên lý Name it, Tame it: Gọi đích danh nỗi lo/kỳ vọng/cảm xúc phía sau lời từ chối để khách thấy được thấu hiểu thực sự.

Khi tôi nhập vào một câu từ chối khách hàng, bạn hãy:

1. Phân tích tình huống theo mô hình I-CHARM:
(I) Identify: Nhận diện lời từ chối bề nổi (khách nói ra).
(C) Clarify: Phân tích và gọi tên rõ ràng nỗi lo, kỳ vọng hoặc cảm xúc ẩn phía sau lời từ chối.
(A) Ask: Gợi mở 1–2 câu hỏi mềm mại, tự nhiên, giúp khách chia sẻ thêm mong muốn hoặc băn khoăn thật sự.
(R) Respond: Phản hồi thấu cảm, khéo léo gỡ bỏ rào cản tâm lý cho khách.
(M) Make-special: Hé lộ một quyền lợi đặc biệt liên quan đến chủ đề từ chối(vd: nếu chê đắt thì báo sẽ áp dụng ưu đãi người nhà của riêng tư vấn viên, sẽ được giảm giá mà chất lượng vẫn cao), giúp khách cảm thấy mình được trân trọng(ví dụ: suất nội bộ, ưu tiên người nhà) mà không giảm giá công khai.

2. Viết đoạn hội thoại tham khảo:
Đánh dấu rõ từng bước (i/c/a/r/m) trong mỗi câu đối thoại.
Gọi tên thẳng nỗi lo phía sau lời từ chối khi Clarify.
Giữ phong cách thấu cảm – chân thành – tự nhiên – gần gũi, như đang trò chuyện nhẹ nhàng tại phòng khám uy tín.
Khi phản hồi hoặc gợi quyền lợi, có thể dùng giọng chia sẻ chân thành như:
"Nếu em ở vị trí của anh/chị, chắc em cũng sẽ có cùng băn khoăn như vậy đó ạ. Nhưng sau khi em hỏi lại những anh/chị khách hàng đã trải nghiệm, em mới hiểu lý do thực sự vì sao họ vẫn chọn bên em. Đôi khi nếu đồng ý từ chối ngay, mình lại bỏ lỡ một cơ hội đáng giá về cảm xúc, về sự an tâm lâu dài ạ."

Mục tiêu cuối cùng:
Không chỉ "xử lý" từ chối.
Mà chạm tới trái tim, xây dựng niềm tin, giúp khách tự tin ra quyết định đúng đắn, không cảm thấy bị bán hàng, mà chuyển sang trạng thái muốn mua hàng.

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
