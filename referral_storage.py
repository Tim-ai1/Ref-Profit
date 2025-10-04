# import aiosqlite
# from aiogram.types import Message
# from shared_data import pending_referrals
# import os
#
#
# DB_PATH = os.getenv('DATABASE_PATH', 'Form.db')
#
#
# async def process_pending_referral(user_id: int, bot, message: Message):
#     # Проверяем в общей переменной
#     if user_id in pending_referrals:
#         referrer_id = pending_referrals[user_id]
#
#         conn = await aiosqlite.connect(DB_PATH)
#         cursor = await conn.cursor()
#
#         try:
#             await cursor.execute('UPDATE Form SET Balance = Balance + 6 WHERE ID = ?', (referrer_id,))
#             await cursor.execute("SELECT Referals FROM Form WHERE ID = ?", (referrer_id,))
#             referals_row = await cursor.fetchone()
#             current_referals = referals_row[0] if referals_row and referals_row[0] else ""
#             new_referals = f"{current_referals} {user_id}".strip()
#             await cursor.execute('UPDATE Form SET Referals = ? WHERE ID = ?', (new_referals, referrer_id))
#             await conn.commit()
#
#             text = f'👋 Вы зарегистрировались по ссылке <a href="tg://user?id={referrer_id}">пользователя</a>\nЕму начислено вознаграждение!'
#             text2 = f'🎉 У вас новый <a href="tg://user?id={user_id}">реферал</a>!\nВам начислено 6 рублей!'
#
#             await cursor.execute("SELECT COUNT(*) FROM Form")
#             number = await cursor.fetchone()
#             await cursor.execute(
#                 "INSERT INTO Form (ID, Code, Balance, Username, "
#                 "Hobbies) VALUES (?, ?, ?, ?)", (message.from_user.id, number[0], 0, message.from_user.username))
#
#             await bot.send_message(chat_id=user_id, text=text, parse_mode='HTML')
#             await bot.send_message(chat_id=referrer_id, text=text2, parse_mode='HTML')
#             await bot.send_message(5262838200, f'😎 Новая <a href="tg://user?id={referrer_id}">регистрация</a>!. ID {referrer_id}',
#                                    parse_mode='HTML')
#             if user_id in pending_referrals:
#                 del pending_referrals[user_id]
#
#         except Exception as e:
#             print(f'Ошибка обработки реферала: {e}')
#         finally:
#             await conn.close()
#     else:
#         print('0200fd')
