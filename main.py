from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from collections import defaultdict

API_TOKEN = 'Your token here'
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# Словарь для хранения данных о пользователях и их ответах
user_data = defaultdict(lambda: {'score': 0, 'nickname': '', 'answers': [], 'completed': False})

quiz = [
    {"question": "Сколько посещений необходимо получить по физкультуре для зачета?",
     "options": ["23", "25", "26"], "correct": 1},
    {"question": "Вставьте пропущенное слово: «Мужество, ….., труд, упорство»",
     "options": ["Честь", "Достоинство", "Воля"], "correct": 2},
    {"question": "Сколько действует паспорт здоровья?",
     "options": ["Год", "Полтора", "Полгода"], "correct": 0},
    {"question": "Когда был основан МГТУ им. Баумана?",
     "options": ["1820 год", "1830 год", "1856 год"], "correct": 1},
    {"question": "Кто является основателем университета?",
     "options": ["Николай Бауман", "Петр I", "Николай II"], "correct": 2},
    {"question": "Дата основания кафедры ИУ10",
     "options": ["07.04.2004", "05.03.2002", "22.04.2006"], "correct": 0},
    {"question": "Кто из известных ученых работал в МГТУ им. Баумана в начале XX века?",
     "options": ["Андрей Туполев", "Сергей Капица", "Сергей Королев"], "correct": 0},
    {"question": "Ответственная за факультет ИУ на кафедре ФВ",
     "options": ["Кривцова Мария Вячеславовна", "Байко Юлия Олеговна", "Жемаева Екатерина Андреевна"], "correct": 0},
    {"question": "На базе какого факультета была создана кафедра ИУ10?",
     "options": ["РЛ", "ИУ", "ЗИ"], "correct": 0},
    {"question": "Диплом о каком образовании есть у Николая Баумана?",
     "options": ["Ветеринар", "Инженер", "Социолог"], "correct": 0},
    {"question": "Чему противодействуют ребята из десятки?",
     "options": ["Грусти", "Скуке", "Смуте"], "correct": 1},
    {"question": "Кто из известных выпускников закончил Бауманку без защиты диплома?",
     "options": ["Шухов", "Королев", "Туполев"], "correct": 0},
    {"question": "В честь кого в названиях самолетов есть сокращение СУ?",
     "options": ["Павел Сухой", "Сумбаев Олег", "Супек Иван"], "correct": 0},
]


# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def start_quiz(message: types.Message):
    user_id = message.from_user.id

    # Проверяем, проходил ли пользователь уже квиз
    if user_data[user_id]['completed']:
        await message.reply("Вы уже прошли этот квиз, повторное прохождение невозможно.")
    else:
        user_data[user_id]['nickname'] = message.from_user.username
        user_data[user_id]['score'] = 0
        user_data[user_id]['answers'] = []
        user_data[user_id]['completed'] = False
        await send_question(user_id, 0)


# Функция для отправки вопросов
async def send_question(user_id, question_index):
    if question_index < len(quiz):
        question = quiz[question_index]
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        for option in question['options']:
            markup.add(KeyboardButton(option))
        await bot.send_message(user_id, question['question'], reply_markup=markup)
    else:
        # Завершение квиза и сообщение пользователю
        user_data[user_id]['completed'] = True
        await bot.send_message(user_id, f"Квиз завершен! Ваши очки: {user_data[user_id]['score']}")


# Обработчик ответов
@dp.message_handler(lambda message: message.text in sum([q['options'] for q in quiz], []))
async def handle_answer(message: types.Message):
    user_id = message.from_user.id
    user_answers = user_data[user_id]['answers']
    question_index = len(user_answers)

    if question_index < len(quiz):
        question = quiz[question_index]
        correct_answer = quiz[question_index]['options'][quiz[question_index]['correct']]

        # Проверка правильности ответа
        if message.text == correct_answer:
            user_data[user_id]['score'] += 1

        # Сохранение ответа пользователя
        user_data[user_id]['answers'].append(message.text)

        # Отправляем следующий вопрос или результат
        await send_question(user_id, question_index + 1)


# Команда для показа топ-20 участников
@dp.message_handler(commands=['top'])
async def show_top(message: types.Message):
    top_users = sorted(user_data.items(), key=lambda x: x[1]['score'], reverse=True)[:20]
    result = "Топ 20 участников:\n"
    for i, (user_id, data) in enumerate(top_users, start=1):
        result += f"{i}. @{data['nickname']} - {data['score']} баллов\n"

    await message.answer(result)


# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)