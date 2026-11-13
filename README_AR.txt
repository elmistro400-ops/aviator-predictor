Aviator Round Tracker — بوت تيليجرام

مهم:
- البوت يسجل النتائج التي تدخلها يدويًا ويحسب إحصائياتها.
- لا يتصل بحساب 1xBet ولا يقرأ اللعبة تلقائيًا.
- لا يستطيع كشف المضاعف القادم أو ضمان التوقع؛ نتائج Crash لا يمكن استنتاجها من النتائج السابقة.

1) أنشئ بوتًا من @BotFather على Telegram:
   - أرسل /newbot
   - اختر اسمًا واسم مستخدم ينتهي بـ bot
   - انسخ TOKEN. لا تشاركه مع أي شخص.

2) تشغيل محلي:
   - ثبّت Python 3.10 أو أحدث.
   - نفّذ: pip install -r requirements.txt
   - عيّن متغير البيئة TELEGRAM_BOT_TOKEN بالتوكن.
   - نفّذ: python bot.py

3) تشغيل 24/7:
   - ارفع محتويات هذا المجلد إلى مستودع GitHub خاص.
   - أنشئ Background Worker على Render واربط المستودع.
   - Build Command: pip install -r requirements.txt
   - Start Command: python bot.py
   - أضف Environment Variable باسم TELEGRAM_BOT_TOKEN وقيمته التوكن.
   - فعّل قرصًا دائمًا أو تخزينًا دائمًا لملف rounds.json إن كان متاحًا في خطتك؛ وإلا قد يضيع السجل عند إعادة النشر.

الأوامر داخل تيليجرام:
 /start
 /add 1.30
 /stats
 /predict
 /last
 /undo
 /clear yes

الأمان:
- لا ترسل كلمة مرور 1xBet أو بيانات الدخول للبوت.
- لا تضع توكن Telegram في كود منشور أو مستودع عام.
