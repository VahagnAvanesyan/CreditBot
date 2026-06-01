print("1. Файл начал выполняться")
import pickle
import numpy as np
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Загружаем модель
with open('loan_model.pkl', 'rb') as f:
    model = pickle.load(f)
    print("2. Модель загружена")

# Шаги диалога
(AGE, INCOME, HOME, EMP_LENGTH, INTENT, GRADE,
 LOAN_AMNT, INT_RATE, PERCENT_INCOME, DEFAULT, CRED_HIST) = range(11)

# Маппинги
HOME_MAP    = {'1': 'RENT', '2': 'OWN', '3': 'MORTGAGE', '4': 'OTHER'}
INTENT_MAP  = {'1': 'PERSONAL', '2': 'EDUCATION', '3': 'MEDICAL',
               '4': 'VENTURE', '5': 'HOMEIMPROVEMENT', '6': 'DEBTCONSOLIDATION'}
GRADE_MAP   = {'1': 'A', '2': 'B', '3': 'C', '4': 'D', '5': 'E', '6': 'F', '7': 'G'}
GRADE_NUM   = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7}
HOME_ENC    = {'RENT': 3, 'OWN': 2, 'MORTGAGE': 0, 'OTHER': 1}
INTENT_ENC  = {'PERSONAL': 4, 'EDUCATION': 1, 'MEDICAL': 3,
               'VENTURE': 5, 'HOMEIMPROVEMENT': 2, 'DEBTCONSOLIDATION': 0}
GRADE_ENC   = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        '👋 Привет! Я помогу узнать, одобрят ли вам кредит.\n\nВведите ваш возраст:'
    )
    return AGE


async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data['age'] = int(update.message.text)
        await update.message.reply_text('💰 Введите ваш годовой доход в долларах (например: 50000):')
        return INCOME
    except:
        await update.message.reply_text('❗ Введите число. Попробуйте снова:')
        return AGE


async def get_income(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data['income'] = int(update.message.text)
        await update.message.reply_text(
            '🏠 Тип жилья:\n1 — Аренда\n2 — Собственное\n3 — Ипотека\n4 — Другое'
        )
        return HOME
    except:
        await update.message.reply_text('❗ Введите число. Попробуйте снова:')
        return INCOME


async def get_home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    val = update.message.text.strip()
    if val not in HOME_MAP:
        await update.message.reply_text('❗ Введите 1, 2, 3 или 4:')
        return HOME
    context.user_data['home'] = HOME_MAP[val]
    await update.message.reply_text('💼 Сколько лет вы работаете? (например: 3):')
    return EMP_LENGTH


async def get_emp_length(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data['emp_length'] = float(update.message.text)
        await update.message.reply_text(
            '🎯 Цель кредита:\n1 — Личные нужды\n2 — Образование\n3 — Медицина\n'
            '4 — Бизнес\n5 — Улучшение жилья\n6 — Погашение долгов'
        )
        return INTENT
    except:
        await update.message.reply_text('❗ Введите число. Попробуйте снова:')
        return EMP_LENGTH


async def get_intent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    val = update.message.text.strip()
    if val not in INTENT_MAP:
        await update.message.reply_text('❗ Введите число от 1 до 6:')
        return INTENT
    context.user_data['intent'] = INTENT_MAP[val]
    await update.message.reply_text('⭐ Кредитный рейтинг (grade):\n1=A  2=B  3=C  4=D  5=E  6=F  7=G')
    return GRADE


async def get_grade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    val = update.message.text.strip()
    if val not in GRADE_MAP:
        await update.message.reply_text('❗ Введите число от 1 до 7:')
        return GRADE
    context.user_data['grade'] = GRADE_MAP[val]
    await update.message.reply_text('💵 Сумма кредита в долларах (например: 10000):')
    return LOAN_AMNT


async def get_loan_amnt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data['loan_amnt'] = int(update.message.text)
        await update.message.reply_text('📈 Процентная ставка по кредиту (например: 12.5):')
        return INT_RATE
    except:
        await update.message.reply_text('❗ Введите число. Попробуйте снова:')
        return LOAN_AMNT


async def get_int_rate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data['int_rate'] = float(update.message.text)
        await update.message.reply_text('📊 Процент дохода на кредит (кредит/доход * 100, например: 20):')
        return PERCENT_INCOME
    except:
        await update.message.reply_text('❗ Введите число. Попробуйте снова:')
        return INT_RATE


async def get_percent_income(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data['percent_income'] = float(update.message.text) / 100
        await update.message.reply_text('⚠️ Были ли у вас дефолты раньше?\n1 — Нет\n2 — Да')
        return DEFAULT
    except:
        await update.message.reply_text('❗ Введите число. Попробуйте снова:')
        return PERCENT_INCOME


async def get_default(update: Update, context: ContextTypes.DEFAULT_TYPE):
    val = update.message.text.strip()
    if val not in ['1', '2']:
        await update.message.reply_text('❗ Введите 1 или 2:')
        return DEFAULT
    context.user_data['default'] = 'N' if val == '1' else 'Y'
    await update.message.reply_text('📅 Сколько лет кредитной истории? (например: 5):')
    return CRED_HIST


async def get_cred_hist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data['cred_hist'] = int(update.message.text)
        return await predict(update, context)
    except:
        await update.message.reply_text('❗ Введите число. Попробуйте снова:')
        return CRED_HIST


async def predict(update: Update, context: ContextTypes.DEFAULT_TYPE):
    d = context.user_data

    features = np.array([[
        d['age'],
        d['income'],
        HOME_ENC[d['home']],
        d['emp_length'],
        INTENT_ENC[d['intent']],
        GRADE_ENC[d['grade']],
        d['loan_amnt'],
        d['int_rate'],
        d['percent_income'],
        1 if d['default'] == 'Y' else 0,
        d['cred_hist']
    ]])

    proba = model.predict_proba(features)[0][1]  # вероятность одобрения

    home_labels  = {'RENT': 'Аренда', 'OWN': 'Собственное', 'MORTGAGE': 'Ипотека', 'OTHER': 'Другое'}
    intent_labels = {'PERSONAL': 'Личные нужды', 'EDUCATION': 'Образование', 'MEDICAL': 'Медицина',
                     'VENTURE': 'Бизнес', 'HOMEIMPROVEMENT': 'Улучшение жилья', 'DEBTCONSOLIDATION': 'Погашение долгов'}

    if proba >= 0.5:
        header = '✅ КРЕДИТ ОДОБРЕН'
        prob_line = f'Вероятность одобрения: {proba*100:.1f}%'
        footer = '🎉 Поздравляем! Ваша заявка соответствует критериям одобрения.'
    else:
        header = '❌ КРЕДИТ ОТКЛОНЁН'
        prob_line = f'Вероятность отклонения: {(1-proba)*100:.1f}%'
        footer = ('⚠️ К сожалению, согласно прогнозу модели, ваша заявка не соответствует '
                  'критериям одобрения.\nРекомендуем обратиться в отделение банка для личной консультации.')

    msg = (
        f'{header}\n\n'
        f'📊 Результат прогноза:\n{prob_line}\n\n'
        f'📋 Ваши параметры:\n'
        f'• Возраст: {d["age"]} лет\n'
        f'• Доход: ${d["income"]:,}\n'
        f'• Тип жилья: {home_labels[d["home"]]}\n'
        f'• Опыт работы: {d["emp_length"]} лет\n'
        f'• Цель кредита: {intent_labels[d["intent"]]}\n'
        f'• Кредитный рейтинг: {d["grade"]}\n'
        f'• Сумма кредита: ${d["loan_amnt"]:,}\n'
        f'• Ставка: {d["int_rate"]}%\n'
        f'• Кредит/доход: {d["percent_income"]*100:.2f}%\n'
        f'• Дефолты: {"Да" if d["default"] == "Y" else "Нет"}\n'
        f'• Кредитная история: {d["cred_hist"]} лет\n\n'
        f'{footer}'
    )

    await update.message.reply_text(msg)
    await update.message.reply_text('Хотите проверить ещё раз? Напишите /start')
    return ConversationHandler.END


# Запуск бота
TOKEN = '8289242206:AAHvNdEdx8qOluQGv5wd0i2fBSFOMk19S7Y'
print("3. Создаем приложение")
app = Application.builder().token(TOKEN).build()

conv = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        AGE:            [MessageHandler(filters.TEXT & ~filters.COMMAND, get_age)],
        INCOME:         [MessageHandler(filters.TEXT & ~filters.COMMAND, get_income)],
        HOME:           [MessageHandler(filters.TEXT & ~filters.COMMAND, get_home)],
        EMP_LENGTH:     [MessageHandler(filters.TEXT & ~filters.COMMAND, get_emp_length)],
        INTENT:         [MessageHandler(filters.TEXT & ~filters.COMMAND, get_intent)],
        GRADE:          [MessageHandler(filters.TEXT & ~filters.COMMAND, get_grade)],
        LOAN_AMNT:      [MessageHandler(filters.TEXT & ~filters.COMMAND, get_loan_amnt)],
        INT_RATE:       [MessageHandler(filters.TEXT & ~filters.COMMAND, get_int_rate)],
        PERCENT_INCOME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_percent_income)],
        DEFAULT:        [MessageHandler(filters.TEXT & ~filters.COMMAND, get_default)],
        CRED_HIST:      [MessageHandler(filters.TEXT & ~filters.COMMAND, get_cred_hist)],
    },
    fallbacks=[CommandHandler('start', start)]
)

app.add_handler(conv)
print('Бот запущен...')
print("4. Запускаем polling")
app.run_polling()