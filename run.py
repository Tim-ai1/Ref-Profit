from aiogram import Dispatcher, F
from aiogram.filters import CommandObject, CommandStart, Command, BaseFilter
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import TelegramObject, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.deep_linking import create_start_link, decode_payload
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
# from referral_storage import process_pending_referral
from admin_panel import *
from dotenv import load_dotenv
import os


load_dotenv()
admin_ids_str = os.getenv('ADMIN_IDS', '')
admins = list(map(int, admin_ids_str.split(','))) if admin_ids_str else []
DB_PATH = os.getenv('DATABASE_PATH', 'Form.db')
channel_ids_str = os.getenv('CHANNELS', '')
CHANNEL_IDS = list(map(int, channel_ids_str.split(','))) if admin_ids_str else []

bot = Bot(TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

class IsAdmin(BaseFilter):
    async def __call__(self, obj: TelegramObject) -> bool:
        return obj.from_user.id in admins



def get_ids():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT ID FROM Form')
    ids = cursor.fetchall()
    ids = [item[0] for item in ids]
    return ids



pending_referrals = {}


async def process_pending_referral(user_id: int, bot, message: Message):
    print(f"DEBUG: process_pending_referral called for user {user_id}")
    print(f"DEBUG: Current pending_referrals: {pending_referrals}")
    print(f"INIT: pending_referrals initially: {pending_referrals}")
    if user_id in pending_referrals:
        referrer_id = pending_referrals[user_id]
        print(f"INIT: pending_referrals initially: {pending_referrals}")
        print(f"DEBUG: Found referral - user: {user_id}, referrer: {referrer_id}")


        conn = await aiosqlite.connect(DB_PATH)
        cursor = await conn.cursor()

        try:
            await cursor.execute('UPDATE Form SET Balance = Balance + 6 WHERE ID = ?', (referrer_id,))
            await cursor.execute("SELECT Referals FROM Form WHERE ID = ?", (referrer_id,))
            referals_row = await cursor.fetchone()
            current_referals = referals_row[0] if referals_row and referals_row[0] else ""
            new_referals = f"{current_referals} {user_id} ".strip()
            await cursor.execute('UPDATE Form SET Referals = ? WHERE ID = ?', (new_referals, referrer_id))
            await conn.commit()

            text = f'👋 Вы зарегистрировались по ссылке <a href="tg://user?id={referrer_id}">пользователя</a>\nЕму начислено вознаграждение!'
            text2 = f'🎉 У вас новый <a href="tg://user?id={user_id}">реферал</a>!\nВам начислено 6 рублей!'

            await cursor.execute("SELECT COUNT(*) FROM Form")
            number = await cursor.fetchone()
            await cursor.execute(
                "INSERT INTO Form (ID, Code, Balance, Username) VALUES (?, ?, ?, ?)", (message.from_user.id, number[0] + 1, 0, message.from_user.username))
            await conn.commit()

            await bot.send_message(chat_id=user_id, text=text, parse_mode='HTML')
            await bot.send_message(chat_id=referrer_id, text=text2, parse_mode='HTML')
            await bot.send_message(5262838200, f'😎 Новая <a href="tg://user?id={referrer_id}">регистрация</a>!. ID {referrer_id}',
                                   parse_mode='HTML')
            if user_id in pending_referrals:
                del pending_referrals[user_id]

        except Exception as e:
            print(f'Ошибка обработки реферала: {e}')
    else:
        conn = await aiosqlite.connect(DB_PATH)
        cursor = await conn.cursor()
        ids = get_ids()
        if message.from_user.id not in ids:
            await cursor.execute("SELECT COUNT(*) FROM Form")
            number = await cursor.fetchone()
            await cursor.execute(
                "INSERT INTO Form (ID, Code, Balance, Username) VALUES (?, ?, ?, ?)",
                (message.from_user.id, number[0] + 1, 0, message.from_user.username))
            await conn.commit()
            await bot.send_message(5262838200,
                                   f'😎 Новая <a href="tg://user?id={message.from_user.id}">регистрация</a>!. ID {message.from_user.id}',
                                   parse_mode='HTML')


async def start(message: Message, command: CommandObject):
    print(f"INIT: pending_referrals initially: {pending_referrals}")
    if not await check_subscription(message.from_user.id, bot):
        return await ask_for_subscription(message)
    print(f"DEBUG: start called for user {message.from_user.id}")
    keyboard = [
        [types.KeyboardButton(text='💵 Работать')],
        [types.KeyboardButton(text='ℹ️ Информация'),
         types.KeyboardButton(text='📢 Задать вопрос')],
        [types.KeyboardButton(text='🚪 Личный кабинет')]
    ]
    reply_markup = types.ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )

    user_id = message.from_user.id
    referrer_id = None

    if command.args:
        try:
            referrer_id = int(decode_payload(command.args))
        except:
            referrer_id = None

    conn = await aiosqlite.connect(DB_PATH)
    cursor = await conn.cursor()

    try:
        await cursor.execute("SELECT ID FROM Form")
        all_ids = [row[0] for row in await cursor.fetchall()]
        print(all_ids)
        print(referrer_id, user_id)
        await cursor.execute("SELECT Referals FROM Form WHERE ID = ?", (referrer_id,))
        referrals_row = await cursor.fetchone()
        current_referrals = referrals_row[0] if referrals_row and referrals_row[0] else ""
        print(current_referrals)
        if referrer_id and referrer_id != user_id and user_id not in all_ids and str(message.from_user.id) not in current_referrals:
            print(1)

            pending_referrals[user_id] = referrer_id
            print(f"INIT: pending_referrals initially: {pending_referrals}")
            print(2)
            print(f"DEBUG: Added to pending_referrals - user: {user_id}, referrer: {referrer_id}")

        # Обрабатываем реферала
        await process_pending_referral(user_id, bot, message)
    except Exception as e:
        await bot.send_message(5262838200, f'Ошибка: {e}')

    ref_link = await create_start_link(bot, payload=str(user_id), encode=True)
    await message.answer(
        f'Ref Profit \n\n👥 Приводите рефералов и зарабатывайте на этом\n💸 Текущий доход за реферала: 5₽ \n\n🔗 Ваша ссылка для '
        f'приглашений:\n\n{ref_link}', parse_mode='HTML')

    ids = get_ids()
    if message.from_user.id not in ids:
        await cursor.execute("SELECT COUNT(*) FROM Form")
        number = await cursor.fetchone()
        await cursor.execute(
            "INSERT INTO Form (ID, Code, Balance, Username) VALUES (?, ?, ?, ?)",
            (message.from_user.id, number[0] + 1, 0, message.from_user.username))
        await conn.commit()


async def rabota(message: Message):
    if not await check_subscription(message.from_user.id, bot):
        return await ask_for_subscription(message)

    user_id = message.from_user.id

    ref_link = await create_start_link(bot, payload=str(user_id), encode=True)
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(
            text="📤 Поделиться ссылкой",
            url=f"https://t.me/share/url?url={ref_link}"
        )]
    ])

    await message.answer(f'👥 Приводите рефералов и зарабатывайте на этом\n💸 Текущий доход за реферала: 5₽ \n\n🔗 Ваша ссылка для '
         f'приглашений:\n\n{ref_link}', reply_markup=keyboard, parse_mode='HTML')


async def lk(message: Message):
    if not await check_subscription(message.from_user.id, bot):
        return await ask_for_subscription(message)
    user_id = message.from_user.id
    conn = await aiosqlite.connect(DB_PATH)
    cursor = await conn.cursor()
    await cursor.execute("SELECT Balance FROM Form WHERE ID = ?", (user_id,))
    bal = await cursor.fetchone()
    await cursor.execute("SELECT Referals FROM Form WHERE ID = ?", (user_id,))
    referrals_row = await cursor.fetchone()
    current_referrals = referrals_row[0] if referrals_row and referrals_row[0] else ""
    count = current_referrals.count(' ') + 1
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='💵 Вывести', callback_data='out')]])
    await message.answer(f'🆔 Ваш ID: <code>{user_id}</code>\n━━━━━━━━━━━━━━━━━━━━━━━━━\n🗣️ Вы пригласили:  '
                         f'{count} рефералов\n💳 Ваш '
                         f'баланс: <b>{bal[0]} руб</b>', parse_mode='HTML', reply_markup=kb)

async def out(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Минимальный вывод: 60 рублей\n\nНапишите сумму которую хотите вывести')
    await state.set_state(Out.money)

async def out2(message: Message, state: FSMContext):
    await state.update_data(mess=message.text)
    conn = await aiosqlite.connect(DB_PATH)
    cursor = await conn.cursor()
    await cursor.execute("SELECT Balance FROM Form WHERE ID = ?", (message.from_user.id,))
    bal = await cursor.fetchone()
    try:
        if int(message.text) >= 60 and bal[0] >= int(message.text):
            await cursor.execute("UPDATE Form SET Balance = ? WHERE ID = ?", (bal[0] - int(message.text), message.from_user.id))
            await conn.commit()
            await message.answer('👍 Ваша заявка отправлена')
            await bot.send_message(5262838200, f'‼️‼️‼️‼️‼️‼️‼️‼️‼️‼️‼️‼️‼️‼️‼️ Пользователь '
                    f'<code>{message.from_user.id}</code> <code>{message.from_user.username}</code> хочет вывести '
                                               f'{message.text} рублей', parse_mode='HTML')
        elif int(message.text) < 60:
            await message.answer('Вы ввели сумму меньше 60 рублей')
        elif bal[0] < int(message.text):
            await message.answer('Вы ввели сумму больше вашего баланса')
    except:
        await message.answer('Введите число')
    await state.clear()



async def info(message: Message):
    if not await check_subscription(message.from_user.id, bot):
        return await ask_for_subscription(message)
    builder = InlineKeyboardBuilder()
    builder.button(text="📢 Канал Ref Profit", url='https://t.me/RefProfit_News')
    keyboard = builder.as_markup()
    await message.answer('ℹ️ Информация\n\nЭто бот Ref Profit. Приглашайте рефералов и зарабатывайте на этом! Ниже '
                         'советы по привлечению рефералов', reply_markup=keyboard)


async def curator(message: Message, state: FSMContext):
    if not await check_subscription(message.from_user.id, bot):
        return await ask_for_subscription(message)

    await message.answer('Введите сообщение, которое хотите отправить куратору')
    await state.set_state(ToCurator.mess)

async def curator2(message: Message, state: FSMContext):
    try:
        for user_id in admins:
            with suppress(Exception):
                if message.photo:
                    caption = message.caption if message.caption else ""
                    await bot.send_photo(chat_id=user_id, photo=message.photo[-1].file_id, caption=caption)
                else:
                    await bot.send_message(chat_id=user_id, text=f'{message.text}\n\nСообщение было отправлено пользователем <code>{message.from_user.id}</code>', parse_mode='HTML')
                await sleep(0.3)

        await message.answer('👽 Сообщение отправлено')
    except Exception as e:
        await message.answer(f'☢️ Ошибка отправки: {str(e)}')
    finally:
        await state.clear()


async def check_subscription(user_id: int, bot: Bot) -> bool:
    for channel_id in CHANNEL_IDS:
        try:
            member = await bot.get_chat_member(channel_id, user_id)
            print(f"Channel: {channel_id}, Status: {member.status}")
            if member.status not in ['member', 'administrator', 'creator']:
                return False
        except Exception as e:
            print(f"Error checking subscription: {e}")
            return False
    return True

async def ask_for_subscription(message: Message):
    t = types.InlineKeyboardButton
    admin_keyboard = [[t(text='Канал №1', url='https://t.me/public_kanal1123')], [t(text='Канал №2', url='https://t.me/print191')],
                      [t(text='Канал №3', url='https://t.me/w12tdfre')]]
    admin_keyboard = types.InlineKeyboardMarkup(inline_keyboard=admin_keyboard)
    await message.answer('Сначала подпишитесь на каналы спонсоров', reply_markup=admin_keyboard)




def register_handlers(dp: Dispatcher):
    dp.message.register(start, CommandStart())

    dp.message.register(rabota, F.text == '💵 Работать')
    dp.message.register(lk, F.text == '🚪 Личный кабинет')
    dp.message.register(info, F.text == 'ℹ️ Информация')
    dp.message.register(curator, F.text == '📢 Задать вопрос')

    dp.message.register(admin_command, Command('admin'), IsAdmin())
    dp.message.register(get_db, F.text == '/db', IsAdmin())

    dp.callback_query.register(newsletter_handler, F.data == 'newsletter')
    dp.message.register(process_newsletter_message, AdminState.newsletter)

    dp.callback_query.register(letter_get_id, F.data == 'letter')
    dp.message.register(letter_get_message, Letter.idd)
    dp.message.register(letter_send_message, Letter.mess)

    dp.callback_query.register(edit_balance, F.data == 'balance')
    dp.message.register(edit_balance2, Balance.idd)
    dp.message.register(edit_balance3, Balance.mess)

    dp.callback_query.register(out, F.data == 'out')
    dp.message.register(out2, Out.money)

    dp.callback_query.register(get_list, F.data == 'list')

    dp.message.register(curator2, ToCurator.mess)