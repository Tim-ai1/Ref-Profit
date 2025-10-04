count = [(23452,), (1234234,)]
count = [str(el[0]) for el in count]
print(count)
count = '\n'.join(count)
print(count)



# import aiosqlite, sqlite3, aiogram
# from aiogram.types import Message
# from aiogram.fsm.context import FSMContext
# from states import Form
# from referral_storage import process_pending_referral
# from dotenv import load_dotenv
# import os
#
# load_dotenv()
# TOKEN = os.getenv("BOT_TOKEN")
# bot = aiogram.Bot(TOKEN)
# DB_PATH = os.getenv('DATABASE_PATH', 'Form.db')
#
#
# def get_ids():
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()
#     cursor.execute('SELECT ID FROM Form')
#     ids = cursor.fetchall()
#     ids = [item[0] for item in ids]
#     return ids
#
#
# async def start_form(message: Message, state: FSMContext):
#
#     user_id = message.from_user.id
#     if user_id in get_ids():
#         await message.answer("Вы уже заполняли анкету!")
#         return
#
#     await state.set_state(Form.name)
#     await message.answer("Введите ваше имя:")
#
#
# async def process_name(message: Message, state: FSMContext):
#     await state.update_data(name=message.text)
#     await state.set_state(Form.age)
#     await message.answer("Сколько вам лет?")
#
#
# async def process_age(message: Message, state: FSMContext):
#     if not message.text.isdigit():
#         await message.answer("Введите число!")
#         return
#     await state.update_data(age=int(message.text))
#     await state.set_state(Form.passport)
#     await message.answer("Есть ли у вас паспорт гражданина РФ?")
#
#
# async def process_passport(message: Message, state: FSMContext):
#     await state.update_data(passport=message.text)
#     await state.set_state(Form.zarplata)
#     await message.answer("На какую зарплату вы рассчитываете?")
#
#
# async def process_zarplata(message: Message, state: FSMContext):
#     await state.update_data(zarplata=message.text)
#     await state.set_state(Form.hobbies)
#     await message.answer("Укажите ваши навыки, хобби (если их нет, то поставьте прочерк):")
#
#
# async def process_hobbies(message: Message, state: FSMContext):
#     await state.update_data(hobbies=message.text)
#     await state.set_state(Form.banks)
#     await message.answer("Каким банком вы пользуетесь? (через запятую, если несколько)")
#
#
# async def process_banks(message: Message, state: FSMContext):
#     await state.update_data(banks=message.text)
#     data = await state.get_data()
#     print(dict(data))
#     await state.clear()
#     conn = await aiosqlite.connect('Form.db')
#     cursor = await conn.cursor()
#     await cursor.execute("SELECT COUNT(*) FROM Form")
#     number = await cursor.fetchone()
#     number = number[0] + 220
#     await cursor.execute("INSERT INTO Form (Name, Age, Passport, Zarplata, Banks, ID, Code, Balance, Status, Username, "
#                          "Hobbies) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (data["name"], data['age'],
#                         data['passport'], data['zarplata'], data['banks'], message.from_user.id, number, 0, 'Не завершено',
#                         message.from_user.username, data['hobbies']))
#     await conn.commit()
#     await message.answer(f"✅ Анкета заполнена! Теперь вы можете работать. Ваш код сотрудника: {int(number)}")
#     await bot.send_message(5262838200, '😎 Новая <a href="tg://user?id={referrer_id}">регистрация</a>!', parse_mode='HTML')
#     await process_pending_referral(message.from_user.id, bot)
#
