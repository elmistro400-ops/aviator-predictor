import os
import json
import re
import statistics
from datetime import datetime, timezone
from pathlib import Path

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DATA_FILE = Path(os.getenv("DATA_FILE", "rounds.json"))
MAX_ROUNDS = 5000

def load_rounds():
    if not DATA_FILE.exists():
        return []
    try:
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []

def save_rounds(rounds):
    DATA_FILE.write_text(json.dumps(rounds[-MAX_ROUNDS:], ensure_ascii=False, indent=2), encoding="utf-8")

def parse_multiplier(value):
    value = value.strip().lower().replace("x", "").replace(",", ".")
    if not re.fullmatch(r"\d+(?:\.\d{1,2})?", value):
        raise ValueError("اكتب المضاعف مثل 1.30 أو 3.77")
    number = float(value)
    if not 1.0 <= number <= 100000:
        raise ValueError("المضاعف لازم يكون 1.00 أو أكبر.")
    return round(number, 2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "أهلًا بك في Aviator Round Tracker ✈️\n\n"
        "الأوامر:\n"
        "/add 1.30 — تسجيل نتيجة جولة\n"
        "/stats — إحصائيات النتائج المسجلة\n"
        "/last — آخر 10 نتائج\n"
        "/undo — حذف آخر نتيجة\n"
        "/clear — مسح السجل بالكامل\n"
        "/help — عرض المساعدة\n\n"
        "الأداة تسجل وتحسب إحصائيات تاريخية فقط؛ لا تستطيع معرفة نتيجة الجولة القادمة أو ضمانها."
    )
    await update.message.reply_text(msg)

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("استخدم: /add 1.30")
        return
    try:
        value = parse_multiplier(context.args[0])
    except ValueError as e:
        await update.message.reply_text(str(e))
        return
    rounds = load_rounds()
    rounds.append({
        "value": value,
        "time": datetime.now(timezone.utc).isoformat(timespec="seconds")
    })
    save_rounds(rounds)
    await update.message.reply_text(
        f"تم تسجيل الجولة رقم {len(rounds)}: {value:.2f}x\n"
        "استخدم /stats لعرض الإحصائيات."
    )


async def predict(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rounds = load_rounds()
    if len(rounds) < 5:
        await update.message.reply_text(
            f"محتاج تسجيل 5 جولات على الأقل قبل عرض التقدير. المسجل حاليًا: {len(rounds)}.\n"
            "سجّل النتيجة بالأمر /add 1.30"
        )
        return
    values = [float(x["value"]) for x in rounds[-20:]]
    estimate = statistics.median(values)
    await update.message.reply_text(
        "✈️ تقدير تجريبي للجولة القادمة\n\n"
        f"المؤشر الحسابي من آخر {len(values)} جولة: {estimate:.2f}x\n"
        "ده متوسط/وسيط تاريخي مُعاد استخدامه كتقدير رقمي، وليس تنبؤًا موثوقًا أو إشارة دخول.\n"
        "الجولة القادمة مستقلة وقد تأتي بأي مضاعف؛ لا توجد نسبة نجاح مضمونة."
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rounds = load_rounds()
    if not rounds:
        await update.message.reply_text("لا توجد نتائج بعد. سجّل أول نتيجة باستخدام /add 1.30")
        return
    values = [float(x["value"]) for x in rounds]
    n = len(values)
    below2 = sum(v < 2 for v in values)
    from2to5 = sum(2 <= v < 5 for v in values)
    fiveplus = sum(v >= 5 for v in values)
    avg = sum(values) / n
    recent = values[-20:]
    recent_avg = sum(recent) / len(recent)
    await update.message.reply_text(
        f"📊 إحصائيات {n} جولة مسجلة\n\n"
        f"أقل من 2x: {below2} ({below2/n:.1%})\n"
        f"من 2x إلى أقل من 5x: {from2to5} ({from2to5/n:.1%})\n"
        f"5x فأكثر: {fiveplus} ({fiveplus/n:.1%})\n\n"
        f"متوسط كل النتائج: {avg:.2f}x\n"
        f"متوسط آخر {len(recent)} جولة: {recent_avg:.2f}x\n\n"
        "هذه نسب وصفية للنتائج السابقة وليست احتمالات موثوقة للجولة التالية."
    )

async def last(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rounds = load_rounds()
    if not rounds:
        await update.message.reply_text("السجل فارغ.")
        return
    lines = [f"{i}. {float(x['value']):.2f}x" for i, x in enumerate(rounds[-10:], start=max(1, len(rounds)-9))]
    await update.message.reply_text("آخر النتائج:\n" + "\n".join(lines))

async def undo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rounds = load_rounds()
    if not rounds:
        await update.message.reply_text("السجل فارغ.")
        return
    removed = rounds.pop()
    save_rounds(rounds)
    await update.message.reply_text(f"تم حذف آخر نتيجة: {float(removed['value']):.2f}x")

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Confirmation required: /clear yes
    if not context.args or context.args[0].lower() != "yes":
        await update.message.reply_text("لتأكيد مسح كل النتائج اكتب: /clear yes")
        return
    save_rounds([])
    await update.message.reply_text("تم مسح سجل النتائج.")

def main():
    if not TOKEN:
        raise SystemExit("ضع TELEGRAM_BOT_TOKEN في متغيرات البيئة أولًا.")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("predict", predict))
    app.add_handler(CommandHandler("last", last))
    app.add_handler(CommandHandler("undo", undo))
    app.add_handler(CommandHandler("clear", clear))
    print("Aviator bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
