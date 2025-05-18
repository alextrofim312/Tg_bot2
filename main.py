from aiogram import Bot, Dispatcher, types, executor

# Вставь сюда токен своего бота
API_TOKEN = '7890476283:AAH9NiicNYmy4Ixghbu19cG8WskeuQN5VV0'
ADMIN_ID = 5726797815  # Замени на свой user_id

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# user_message_map: message_id у админа -> user_id пользователя
user_message_map = {}

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply(
        "Hi! If you need language learning materials, write to the bot. The admin will answer you.")

# Для любых вложений/сообщений пользователей
@dp.message_handler(lambda message: message.chat.id != ADMIN_ID, content_types=types.ContentTypes.ANY)
async def handle_any_user_message(message: types.Message):
    sender = f"@{message.from_user.username}" if message.from_user.username else f"id: {message.from_user.id}"

    # Для текста
    if message.text:
        sent = await bot.send_message(ADMIN_ID, f"Сообщение от {sender}:\n{message.text}")
    # Для фото
    elif message.photo:
        caption = message.caption or ""
        sent = await bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=f"Фото от {sender}:\n{caption}")
    # Для документов
    elif message.document:
        caption = message.caption or ""
        sent = await bot.send_document(ADMIN_ID, message.document.file_id, caption=f"Документ от {sender}:\n{caption}")
    # Для аудиофайлов
    elif message.audio:
        sent = await bot.send_audio(ADMIN_ID, message.audio.file_id, caption=f"Аудио от {sender}")
    # Для голосовых
    elif message.voice:
        sent = await bot.send_voice(ADMIN_ID, message.voice.file_id, caption=f"Голосовое от {sender}")
    # Для видео
    elif message.video:
        caption = message.caption or ""
        sent = await bot.send_video(ADMIN_ID, message.video.file_id, caption=f"Видео от {sender}:\n{caption}")
    # Если ничего из выше (например, стикер)
    else:
        sent = await bot.send_message(ADMIN_ID, f"[Неподдерживаемый тип сообщения] от {sender}")

    # Сохраняем соответствие для ответа
    user_message_map[sent.message_id] = message.chat.id

# Ответ админа пользователю (поддержка вложений)
@dp.message_handler(lambda message: message.chat.id == ADMIN_ID, is_reply=True, content_types=types.ContentTypes.ANY)
async def reply_from_admin(message: types.Message):
    reply_to_id = message.reply_to_message.message_id
    user_id = user_message_map.get(reply_to_id)
    if not user_id:
        await message.reply('Не удалось определить пользователя для ответа.')
        return

    # Ответы пользователю поддерживают разные типы вложений
    if message.text:
        await bot.send_message(user_id, message.text)
    elif message.photo:
        await bot.send_photo(user_id, message.photo[-1].file_id, caption=message.caption)
    elif message.document:
        await bot.send_document(user_id, message.document.file_id, caption=message.caption)
    elif message.audio:
        await bot.send_audio(user_id, message.audio.file_id, caption=message.caption)
    elif message.voice:
        await bot.send_voice(user_id, message.voice.file_id)
    elif message.video:
        await bot.send_video(user_id, message.video.file_id, caption=message.caption)
    else:
        await message.reply("Этот тип ответа пока не поддерживается.")

    await message.reply('Ответ отправлен!')

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
