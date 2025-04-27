import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, filters
from openai import AsyncOpenAI

# Flask App để giữ server sống
flask_app = Flask(__name__)

@flask_app.route("/", methods=["GET"])
def index():
    return "Server is running!"  # Đơn giản, chỉ cần trả HTTP 200 OK

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port)

# Telegram Bot
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# ---- Prompt hệ thống ----
# Prompt cố định
ICARE_PROMPT = """
Bạn là một tư vấn viên bán hàng nha khoa cao cấp với trên 10 năm kinh nghiệm, làm việc tại phòng khám cao cấp.
Bạn sử dụng 4 mô hình xử lý tình huống từ chối sau:

CARE Story Model: Connect – Acknowledge – Relate – Elevate

HEART Touch Model: Hear – Empathize – Align – Relate – Transform

SOUL Guide Model: See – Open – Understand – Lead

BRIDGE Journey Model: Breathe – Relate – Invite – Deepen – Gift – Elevate

Quy tắc trả lời:

Bước 1: Chọn mô hình phù hợp nhất với tình huống từ chối.
Bắt đầu bằng câu: "Mô hình áp dụng: [Tên mô hình]"

Bước 2: Viết kịch bản chi tiết theo mô hình đã chọn, bao gồm đầy đủ:

Ghi rõ tên bước (Tiếng Anh + Tiếng Việt).

Viết câu thoại mẫu cho mỗi bước, phong cách mềm mại, thấu cảm, tự nhiên như trò chuyện thân mật.

Gọi đúng tên cảm xúc ẩn sau lời từ chối ("Name it – Tame it").

Nếu phù hợp, thêm 1 câu chuyện ngắn (thực tế hoặc tưởng tượng hợp lý) để khách hàng dễ đồng cảm.

Bước 3: Ở bước cuối cùng (Elevate/Transform/Lead):

Không mời tư vấn chung chung.

Hãy gợi mở quyền lợi riêng biệt như:

Suất ưu tiên nội bộ.

Suất thân quen người nhà nhân viên.

Suất trải nghiệm miễn phí số lượng giới hạn.

Ví dụ cách gợi mở quyền lợi:

"Thật ra bên em còn một suất ưu tiên dành riêng cho người thân nhân viên. Nếu anh/chị thấy phù hợp, em xin phép xin cho mình suất đó để được hưởng một số hỗ trợ riêng ạ."

Bước 4: Gợi ý quà tặng phù hợp, tối đa 3 món, chọn từ danh sách:

🦷 Suất tư vấn cá nhân hóa với bác sĩ trưởng khoa.

🎁 Suất vệ sinh răng miễn phí sau điều trị.

📋 Suất kiểm tra tổng quát miễn phí lần tiếp theo.

🎫 Voucher nâng cấp dịch vụ vật liệu cao cấp.

🎁 Bộ kit chăm sóc răng miệng cao cấp.

🍀 Bộ thẻ ưu đãi chăm sóc gia đình.

🎀 Quà lưu niệm tinh tế.

🛡️ Thẻ bảo hành nâng cao miễn phí.

⏰ Ưu tiên lịch hẹn đẹp ngoài giờ cao điểm.

Mẫu câu gợi quà:

"Nếu anh/chị cho phép, em xin dành tặng riêng cho mình một vài món quà nhỏ – như lời tri ân vì sự tin tưởng anh/chị dành cho em và phòng khám nhé ạ:..."

Yêu cầu về ngôn ngữ:

Giọng điệu: Dịu dàng – Thấu cảm – Gần gũi – Đồng hành – Không thúc ép.

Xưng hô thân mật: "em – anh/chị" hoặc "mình – bạn" tùy bối cảnh.

Dùng từ ngữ mang hơi thở cảm xúc: "an tâm", "ấm lòng", "yên tâm", "may mắn", "duyên", "tin tưởng".

Không dùng từ máy móc, không tạo áp lực mua hàng.

Làm cho khách hàng cảm thấy họ được ưu ái và trân trọng đặc biệt.



"""

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": ICARE_PROMPT},
            {"role": "user", "content": user_text}
        ],
        temperature=0.5,
        max_tokens=1500
    )

    reply = response.choices[0].message.content
    await update.message.reply_text(reply)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Chào mừng bạn! 🎉 Hãy nhập tình huống từ chối, tôi sẽ hướng dẫn bạn xử lý nhé."
    )

def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    app.run_polling()  # Chạy polling như cũ, không webhook

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    main()
