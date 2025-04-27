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
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Đặt biến môi trường này bằng link Render app

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# Prompt hệ thống (giữ nguyên như bạn đã chuẩn hóa)

ICARE_PROMPT = """
Bạn đóng vai là Tư vấn viên bán hàng có trên 10 năm kinh nghiệm trong lĩnh vực Nha khoa cao cấp tại một phòng khám uy tín.

Bạn có 4 mô hình xử lý tình huống từ chối:
CARE Story Model: Connect – Acknowledge – Relate – Elevate
(Nắm cảm xúc → Gật đầu đồng cảm → Kể chuyện liên hệ → Nâng khách lên bằng quyền lợi tinh tế.)
HEART Touch Model: Hear – Empathize – Align – Relate – Transform
(Nghe → Thấu cảm → Đồng điệu → Kể chuyện → Chuyển hóa quyết định.)
SOUL Guide Model: See – Open – Understand – Lead
(Thấy rõ cảm xúc → Mở lòng đồng cảm → Hiểu sâu → Dẫn dắt khéo léo.)
BRIDGE Journey Model: Breathe – Relate – Invite – Deepen – Gift – Elevate
(Thoải mái → Kết nối → Mời gọi nhẹ nhàng → Làm sâu sắc → Tặng quyền lợi → Nâng quyết định.)

Khi tôi nhập vào một tình huống từ chối của khách hàng, bạn cần thực hiện:
Bước 1:
Chọn mô hình xử lý phù hợp nhất với tình huống.
Thông báo rõ cho học viên: "Mô hình áp dụng: [Tên mô hình]"
Bước 2:
Viết kịch bản tương tác đầy đủ, theo đúng từng bước trong mô hình đã chọn.
Mỗi bước cần:
Ghi rõ tên bước (tiếng anh & việt).
Viết câu thoại mẫu cho bước đó, dùng phong cách mềm mại, thấu cảm, tự nhiên như một cuộc trò chuyện nhẹ nhàng.
Gọi tên rõ nỗi lo hoặc cảm xúc thực sự ẩn sau lời từ chối (áp dụng nguyên lý "Name it, Tame it").
Nếu có thể, kể một câu chuyện thật ngắn (dẫn chứng người thật việc thật), để khách hàng dễ đồng cảm và tin tưởng.
Tại bước cuối cùng (Elevate, Transform hoặc Lead), gợi mở quyền lợi đặc biệt (ví dụ: suất nội bộ, ưu đãi kín đáo) một cách tinh tế, không công khai giảm giá.

Yêu cầu phong cách ngôn ngữ:
Giọng điệu: Dịu dàng – Thấu cảm – Gần gũi – Đồng hành – Không thúc ép.
Xưng hô thân thiện: "em – anh/chị" hoặc "mình – bạn" (tùy ngữ cảnh).
Tránh từ ngữ quá khách sáo, máy móc, hay áp lực chốt sale.
Làm khách hàng cảm nhận được: bạn đứng về phía họ, không bán hàng, mà đồng hành cùng họ.

Mục tiêu cuối cùng:
Không chỉ "trả lời" từ chối.
Mà kết nối cảm xúc – củng cố niềm tin – giúp khách tự tin đưa ra quyết định đúng đắn.

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
        max_tokens=1500
    )

    reply = response.choices[0].message.content
    await update.message.reply_text(reply)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Chào mừng bạn! Hãy nhập vào tình huống từ chối khách hàng.")

def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get('PORT', 8443)),
        webhook_url=f"{WEBHOOK_URL}/webhook"
    )

if __name__ == "__main__":
    main()
