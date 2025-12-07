import telebot
import time
import threading
import json
import os
from collections import defaultdict

# ============ НАСТРОЙКИ ============
BOT_TOKEN = "8328271974:AAGZUdEpdB0fgMh0Rn6nU6kLItDPUV1peYg"
GROUP_ID = -1003401534273
GROUP_LINK = "https://t.me/your_group_link"

# Админы (указывайте ID вручную)
ADMIN_IDS = [8133343248]  # ⬅️ ВАШ ID ЗДЕСЬ!

print(f"👑 Загружено админов: {len(ADMIN_IDS)}")
print(f"🆔 Админы: {ADMIN_IDS}")

# ============ ИНИЦИАЛИЗАЦИЯ ============
try:
    bot = telebot.TeleBot(BOT_TOKEN)
    bot.get_me()
    print("✅ Бот запущен")
except:
    print("❌ Ошибка токена!")
    exit()

# Анти-спам система
user_messages = defaultdict(list)
MUTE_THRESHOLD = 3
TIME_WINDOW = 1
MUTE_DURATION = 600

# ============ ФУНКЦИИ ============

def delete_after(chat_id, message_id, delay=60):
    """Удалить сообщение через N секунд"""
    time.sleep(delay)
    try:
        bot.delete_message(chat_id, message_id)
    except:
        pass

def send_and_delete(message, text, delay=60, reply_to=False):
    """Отправить и удалить через время"""
    try:
        if reply_to:
            msg = bot.reply_to(message, text)
        else:
            msg = bot.send_message(message.chat.id, text)
        
        threading.Thread(target=delete_after, args=(message.chat.id, msg.message_id, delay)).start()
        return msg
    except Exception as e:
        # Если не удалось ответить на сообщение (например, оно удалено), отправляем обычное сообщение
        try:
            msg = bot.send_message(message.chat.id, text)
            threading.Thread(target=delete_after, args=(message.chat.id, msg.message_id, delay)).start()
            return msg
        except:
            return None

# ============ КОМАНДЫ ============

# /start
@bot.message_handler(commands=['start'])
def start_handler(message):
    if message.chat.type == 'private':
        text = f"""🤖 *Бот для группы* {GROUP_LINK}

🛡 *Модерация:* mute, ban, kick, info
👑 *Админы:* предустановлены в коде
🎵 *Запросы:* !golos [песня]
⚠️ *Жалобы:* !report [причина]

📋 *Все команды:* !команды"""
        bot.send_message(message.chat.id, text, parse_mode='Markdown')

# !команды
@bot.message_handler(func=lambda m: m.text and m.text.lower() in ['!команды', '!help'] and m.chat.id == GROUP_ID)
def commands_handler(message):
    # Удаляем сообщение админа
    if message.from_user.id in ADMIN_IDS:
        try:
            bot.delete_message(message.chat.id, message.message_id)
        except:
            pass
    
    text = """🎮 *КОМАНДЫ*

🎵 *Запрос песни:*
`!golos Queen - Bohemian Rhapsody`
`!golos` (в ответ на аудио)

⚠️ *Жалобы (в ответ):*
`!report спам`
`!report оскорбление`
`!report реклама`

👮 *Админам (в ответ или по ID):*
`!info` - инфо в ЛС
`!mute 5` - мут на 5 мин (в ответ)
`!mute 123456 60` - мут ID на 60 мин
`!unmute` - размут (в ответ)
`!unmute 123456` - размут по ID
`!ban` - бан (в ответ)
`!ban 123456` - бан по ID
`!unban 123456` - разбан по ID
`!kick` - кик (в ответ)

🤖 *Проверка бота:*
`!просыпайся` - проверить работу"""
    
    # Для админов не используем reply_to (сообщение удалено), для обычных пользователей - используем
    if message.from_user.id in ADMIN_IDS:
        send_and_delete(message, text, 30, reply_to=False)
    else:
        send_and_delete(message, text, 30, reply_to=True)

# !просыпайся
@bot.message_handler(func=lambda m: m.text and m.text.lower() in ['!просыпайся', '!проверка', '!ping'] and m.chat.id == GROUP_ID)
def wakeup_handler(message):
    # Удаляем сообщение админа
    if message.from_user.id in ADMIN_IDS:
        try:
            bot.delete_message(message.chat.id, message.message_id)
        except:
            pass
    
    replies = [
        "🤖 Я здесь! Бот работает исправно!",
        "✅ Всё в порядке, я на связи!",
        "⚡ Бот активен и готов к работе!",
        "🎮 На месте! Команды готовы к использованию!"
    ]
    import random
    reply = random.choice(replies)
    
    # Для админов не используем reply_to (сообщение удалено), для обычных пользователей - используем
    if message.from_user.id in ADMIN_IDS:
        send_and_delete(message, reply, 60, reply_to=False)
    else:
        send_and_delete(message, reply, 60, reply_to=True)

# !golos
@bot.message_handler(func=lambda m: m.text and m.text.startswith('!golos') and m.chat.id == GROUP_ID)
def golos_handler(message):
    # Удаляем сообщение админа
    if message.from_user.id in ADMIN_IDS:
        try:
            bot.delete_message(message.chat.id, message.message_id)
        except:
            pass
    
    user = message.from_user
    
    if message.reply_to_message:
        msg = message.reply_to_message
        if msg.audio:
            song = f"{msg.audio.performer or ''} - {msg.audio.title or 'Аудио'}"
        elif msg.text:
            song = msg.text[:200]
        else:
            song = "Медиа-контент"
    else:
        song = message.text.replace('!golos', '', 1).strip()
        if not song:
            # Для админов не используем reply_to (сообщение удалено), для обычных пользователей - используем
            if message.from_user.id in ADMIN_IDS:
                send_and_delete(message, "❌ Укажите песню!\n`!golos Nirvana - Smells Like Teen Spirit`", reply_to=False)
            else:
                send_and_delete(message, "❌ Укажите песню!\n`!golos Nirvana - Smells Like Teen Spirit`", reply_to=True)
            return
    
    text = f"""🎵 *ЗАПРОС ПЕСНИ*
👤 @{user.username or user.first_name}
🎶 {song[:300]}
🕒 {time.strftime('%H:%M')}"""
    
    for admin_id in ADMIN_IDS:
        try:
            bot.send_message(admin_id, text, parse_mode='Markdown')
        except:
            pass
    
    # Для админов не используем reply_to (сообщение удалено), для обычных пользователей - используем
    if message.from_user.id in ADMIN_IDS:
        send_and_delete(message, "✅ Запрос отправлен!", reply_to=False)
    else:
        send_and_delete(message, "✅ Запрос отправлен!", reply_to=True)

# !report
@bot.message_handler(func=lambda m: m.text and m.text.startswith('!report') and m.chat.id == GROUP_ID)
def report_handler(message):
    # Удаляем сообщение админа
    if message.from_user.id in ADMIN_IDS:
        try:
            bot.delete_message(message.chat.id, message.message_id)
        except:
            pass
    
    if not message.reply_to_message:
        # Для админов не используем reply_to (сообщение удалено), для обычных пользователей - используем
        if message.from_user.id in ADMIN_IDS:
            send_and_delete(message, "❌ Ответьте на сообщение!\n`!report спам`", reply_to=False)
        else:
            send_and_delete(message, "❌ Ответьте на сообщение!\n`!report спам`", reply_to=True)
        return
    
    parts = message.text.split()
    reason = "нарушение"
    if len(parts) > 1:
        reason = ' '.join(parts[1:])
    
    user = message.from_user
    target = message.reply_to_message.from_user
    
    text = f"""⚠️ *ЖАЛОБА*
👤 От: @{user.username or user.first_name}
👥 На: @{target.username or target.first_name}
📌 Причина: {reason}
🆔 ID: `{target.id}`
🕒 {time.strftime('%H:%M')}"""
    
    for admin_id in ADMIN_IDS:
        try:
            bot.send_message(admin_id, text, parse_mode='Markdown')
        except:
            pass
    
    # Для админов не используем reply_to (сообщение удалено), для обычных пользователей - используем
    if message.from_user.id in ADMIN_IDS:
        send_and_delete(message, "✅ Жалоба отправлена!", reply_to=False)
    else:
        send_and_delete(message, "✅ Жалоба отправлена!", reply_to=True)

# !info
@bot.message_handler(func=lambda m: m.text and m.text.startswith('!info') and m.chat.id == GROUP_ID)
def info_handler(message):
    if message.from_user.id not in ADMIN_IDS:
        return
    
    # Удаляем сообщение админа
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except:
        pass
    
    if not message.reply_to_message:
        # Сообщение админа уже удалено, используем обычное сообщение
        send_and_delete(message, "❌ Ответьте на сообщение!", reply_to=False)
        return
    
    target = message.reply_to_message.from_user
    text = f"""👤 *{target.first_name}*
{"📛 " + target.last_name if target.last_name else ""}
{"🔗 @" + target.username if target.username else ""}
🆔 `{target.id}`"""
    
    try:
        bot.send_message(message.from_user.id, text, parse_mode='Markdown')
        send_and_delete(message, "✅ Инфо в ЛС!", reply_to=False)
    except:
        send_and_delete(message, "❌ Напишите /start боту", reply_to=False)

# !ban
@bot.message_handler(func=lambda m: m.text and m.text.startswith('!ban') and m.chat.id == GROUP_ID)
def ban_handler(message):
    if message.from_user.id not in ADMIN_IDS:
        return
    
    parts = message.text.split()
    admin = message.from_user
    
    # Удаляем сообщение админа
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except:
        pass
    
    # Бан по ID
    if len(parts) > 1 and parts[1].isdigit():
        user_id = int(parts[1])
        try:
            bot.ban_chat_member(GROUP_ID, user_id)
            bot.send_message(GROUP_ID, f"🚷 Администратор @{admin.username or admin.first_name} заблокировал ID `{user_id}`")
        except:
            bot.send_message(GROUP_ID, f"❌ Ошибка бана ID `{user_id}`")
        return
    
    # Бан в ответ
    if not message.reply_to_message:
        bot.send_message(GROUP_ID, "❌ Ответьте на сообщение или укажите ID!\n`!ban 123456`")
        return
    
    target = message.reply_to_message.from_user
    if target.id in ADMIN_IDS:
        bot.send_message(GROUP_ID, "❌ Нельзя забанить админа!")
        return
    
    try:
        bot.ban_chat_member(GROUP_ID, target.id)
        target_name = f"@{target.username or target.first_name}"
        bot.send_message(GROUP_ID, f"🚷 Администратор @{admin.username or admin.first_name} заблокировал {target_name}")
    except:
        bot.send_message(GROUP_ID, "❌ Ошибка!")

# !unban
@bot.message_handler(func=lambda m: m.text and m.text.startswith('!unban') and m.chat.id == GROUP_ID)
def unban_handler(message):
    if message.from_user.id not in ADMIN_IDS:
        return
    
    parts = message.text.split()
    admin = message.from_user
    
    # Удаляем сообщение админа
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except:
        pass
    
    # Разбан по ID
    if len(parts) > 1 and parts[1].isdigit():
        user_id = int(parts[1])
        try:
            bot.unban_chat_member(GROUP_ID, user_id)
            bot.send_message(GROUP_ID, f"✅ Администратор @{admin.username or admin.first_name} разблокировал ID `{user_id}`")
        except:
            bot.send_message(GROUP_ID, f"❌ Ошибка разбана ID `{user_id}`")
        return
    
    # Разбан в ответ
    if not message.reply_to_message:
        bot.send_message(GROUP_ID, "❌ Ответьте на сообщение или укажите ID!\n`!unban 123456`")
        return
    
    target = message.reply_to_message.from_user
    try:
        bot.unban_chat_member(GROUP_ID, target.id)
        target_name = f"@{target.username or target.first_name}"
        bot.send_message(GROUP_ID, f"✅ Администратор @{admin.username or admin.first_name} разблокировал {target_name}")
    except:
        bot.send_message(GROUP_ID, "❌ Ошибка!")

# !mute
@bot.message_handler(func=lambda m: m.text and m.text.startswith('!mute') and m.chat.id == GROUP_ID)
def mute_handler(message):
    if message.from_user.id not in ADMIN_IDS:
        return
    
    parts = message.text.split()
    admin = message.from_user
    
    # Удаляем сообщение админа
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except:
        pass
    
    # Мут по ID
    if len(parts) > 2 and parts[1].isdigit() and parts[2].isdigit():
        user_id = int(parts[1])
        minutes = int(parts[2])
        
        if user_id in ADMIN_IDS:
            bot.send_message(GROUP_ID, "❌ Нельзя замутить админа!")
            return
        
        seconds = max(1, minutes) * 60
        
        try:
            bot.restrict_chat_member(GROUP_ID, user_id, until_date=int(time.time()) + seconds, can_send_messages=False)
            
            if minutes < 60:
                time_text = f"{minutes}м"
            elif minutes < 1440:
                hours = minutes // 60
                time_text = f"{hours}ч"
            else:
                days = minutes // 1440
                time_text = f"{days}д"
            
            bot.send_message(GROUP_ID, f"🔇 Администратор @{admin.username or admin.first_name} замутил ID `{user_id}` на {time_text}")
        except:
            bot.send_message(GROUP_ID, f"❌ Ошибка мута ID `{user_id}`")
        return
    
    # Мут в ответ
    if not message.reply_to_message:
        bot.send_message(GROUP_ID, "❌ Ответьте на сообщение или укажите ID и время:\n`!mute 123456 60`")
        return
    
    target = message.reply_to_message.from_user
    if target.id in ADMIN_IDS:
        bot.send_message(GROUP_ID, "❌ Нельзя замутить админа!")
        return
    
    minutes = 60
    if len(parts) > 1 and parts[1].isdigit():
        minutes = int(parts[1])
    
    seconds = max(1, minutes) * 60
    
    try:
        bot.restrict_chat_member(GROUP_ID, target.id, until_date=int(time.time()) + seconds, can_send_messages=False)
        
        if minutes < 60:
            time_text = f"{minutes}м"
        elif minutes < 1440:
            hours = minutes // 60
            time_text = f"{hours}ч"
        else:
            days = minutes // 1440
            time_text = f"{days}д"
        
        target_name = f"@{target.username or target.first_name}"
        bot.send_message(GROUP_ID, f"🔇 Администратор @{admin.username or admin.first_name} замутил {target_name} на {time_text}")
    except:
        bot.send_message(GROUP_ID, "❌ Ошибка!")

# !unmute
@bot.message_handler(func=lambda m: m.text and m.text.startswith('!unmute') and m.chat.id == GROUP_ID)
def unmute_handler(message):
    if message.from_user.id not in ADMIN_IDS:
        return
    
    parts = message.text.split()
    admin = message.from_user
    
    # Удаляем сообщение админа
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except:
        pass
    
    # Размут по ID
    if len(parts) > 1 and parts[1].isdigit():
        user_id = int(parts[1])
        try:
            bot.restrict_chat_member(GROUP_ID, user_id, can_send_messages=True)
            bot.send_message(GROUP_ID, f"🔊 Администратор @{admin.username or admin.first_name} размутил ID `{user_id}`")
        except:
            bot.send_message(GROUP_ID, f"❌ Ошибка размута ID `{user_id}`")
        return
    
    # Размут в ответ
    if not message.reply_to_message:
        bot.send_message(GROUP_ID, "❌ Ответьте на сообщение или укажите ID:\n`!unmute 123456`")
        return
    
    target = message.reply_to_message.from_user
    try:
        bot.restrict_chat_member(GROUP_ID, target.id, can_send_messages=True)
        target_name = f"@{target.username or target.first_name}"
        bot.send_message(GROUP_ID, f"🔊 Администратор @{admin.username or admin.first_name} размутил {target_name}")
    except:
        bot.send_message(GROUP_ID, "❌ Ошибка!")

# !kick
@bot.message_handler(func=lambda m: m.text and (m.text.startswith('!kick') or m.text.startswith('!vis')) and m.chat.id == GROUP_ID)
def kick_handler(message):
    if message.from_user.id not in ADMIN_IDS:
        return
    
    if not message.reply_to_message:
        return
    
    admin = message.from_user
    target = message.reply_to_message.from_user
    
    # Удаляем сообщение админа
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except:
        pass
    
    if target.id in ADMIN_IDS:
        bot.send_message(GROUP_ID, "❌ Нельзя кикнуть админа!")
        return
    
    try:
        bot.delete_message(GROUP_ID, message.reply_to_message.message_id)
        bot.ban_chat_member(GROUP_ID, target.id)
        time.sleep(1)
        bot.unban_chat_member(GROUP_ID, target.id)
        target_name = f"@{target.username or target.first_name}"
        bot.send_message(GROUP_ID, f"👢 Администратор @{admin.username or admin.first_name} кикнул {target_name}")
    except:
        bot.send_message(GROUP_ID, "❌ Ошибка кика!")

# ============ АНТИ-СПАМ ============
@bot.message_handler(func=lambda m: m.chat.id == GROUP_ID)
def anti_spam(message):
    user_id = message.from_user.id
    
    # Игнорируем админов
    if user_id in ADMIN_IDS:
        return
    
    # Игнорируем команды
    if message.text and message.text.startswith('!'):
        return
    
    # Анти-спам проверка
    now = time.time()
    user_messages[user_id].append(now)
    
    # Очищаем старые сообщения
    user_messages[user_id] = [t for t in user_messages[user_id] if now - t < TIME_WINDOW]
    
    # Если больше порога - мут
    if len(user_messages[user_id]) > MUTE_THRESHOLD:
        try:
            bot.restrict_chat_member(
                GROUP_ID, 
                user_id, 
                until_date=int(now) + MUTE_DURATION,
                can_send_messages=False
            )
            bot.send_message(
                GROUP_ID, 
                f"⚠️ @{message.from_user.username or message.from_user.first_name} получил мут на 10 минут за спам!"
            )
            # Очищаем историю
            user_messages[user_id] = []
        except:
            pass

# ============ ЗАПУСК ============
if __name__ == '__main__':
    print("=" * 50)
    print("🤖 БОТ ЗАПУЩЕН")
    print("=" * 50)
    print(f"👥 Группа: {GROUP_ID}")
    print(f"👑 Админы: {len(ADMIN_IDS)} пользователь(ей)")
    print(f"🛡 Анти-спам: {MUTE_THRESHOLD} смс/{TIME_WINDOW}сек")
    print("=" * 50)
    print("⚡ Ожидание сообщений...")
    print("=" * 50)
    bot.infinity_polling()