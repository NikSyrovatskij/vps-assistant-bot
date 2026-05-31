import asyncio
import os
import paramiko
import httpx  # Для связи с локальным API
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

import database as db

# --- Настройка состояний ---
class AddServer(StatesGroup):
    waiting_for_name = State()
    waiting_for_ip = State()
    waiting_for_user = State()
    waiting_for_password = State()

TOKEN = os.getenv("BOT_TOKEN")
API_URL = os.getenv("API_URL", "http://api:8000/status") # URL нашего FastAPI

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

db.init_db()

# --- Клавиатура ---
def get_main_keyboard():
    buttons = [
        [KeyboardButton(text="📊 Статус серверов")],
        [KeyboardButton(text="🖥 Мой хост")], # Новая кнопка
        [KeyboardButton(text="➕ Добавить сервер"), KeyboardButton(text="📋 Список серверов")],
        [KeyboardButton(text="❌ Удалить сервер")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

# --- Обработка "Мой хост" (через FastAPI) ---
@dp.message(F.text == "🖥 Мой хост")
async def cmd_host_status(message: types.Message):
    try:
        async with httpx.AsyncClient() as client:
            # Запрос к нашему сервису api
            response = await client.get(API_URL, timeout=5.0)
            data = response.json()

        text = (
            f"🏠 <b>Статус хост-сервера (локально):</b>\n\n"
            f"<b>Система:</b> {data['system']} {data['release']}\n"
            f"<b>Аптайм:</b> {data['uptime']}\n\n"
            f"<b>CPU:</b> <code>{data['cpu_usage']}%</code> (ядер: {data['cpu_count']})\n"
            f"<b>RAM:</b> <code>{data['ram']['used']}</code> / <code>{data['ram']['total']}</code> ({data['ram']['percent']}%)\n"
            f"<b>Disk:</b> <code>{data['disk']['used']}</code> / <code>{data['disk']['total']}</code> ({data['disk']['percent']}%)"
        )
    except Exception as e:
        text = f"❌ Ошибка связи с локальным API: {e}"

    await message.answer(text)

# --- Остальные функции (оставляем как были) ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Привет! Я твой VPS-ассистент.\nИспользуй кнопки внизу для управления.",
        reply_markup=get_main_keyboard()
    )

@dp.message(F.text == "➕ Добавить сервер")
@dp.message(Command("add_server"))
async def start_add_server(message: types.Message, state: FSMContext):
    await message.answer("📝 Введите название сервера:")
    await state.set_state(AddServer.waiting_for_name)

@dp.message(F.text == "📋 Список серверов")
@dp.message(Command("list_servers"))
async def list_servers(message: types.Message):
    servers = db.get_servers(message.from_user.id)
    if not servers:
        await message.answer("Список серверов пуст.")
        return
    text = "📂 <b>Ваши серверы:</b>\n\n"
    for s in servers:
        text += f"🆔 <code>{s[0]}</code> | <b>{s[1]}</b> ({s[2]})\n"
    await message.answer(text)

@dp.message(Command("remove_server"))
async def remove_server(message: types.Message):
    try:
        server_id = int(message.text.split()[1])
        db.delete_server(server_id, message.from_user.id)
        await message.answer(f"🗑 Сервер {server_id} удален.")
    except:
        await message.answer("Введите: /remove_server ID")

# --- SSH Логика для удаленных серверов ---
def get_detailed_status(ip, user, password):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=ip, username=user, password=password, timeout=10)
        commands = (
            "uptime -p || echo 'N/A'; "
            "grep 'model name' /proc/cpuinfo | head -n 1 | cut -d':' -f2 || echo 'N/A'; "
            "cat /proc/loadavg | awk '{print $1}' || echo 'N/A'; "
            "free -m | awk 'NR==2{printf \"RAM: %s/%s MB (%.1f%%)\", $3,$2,$3*100/$2}' || echo 'N/A'; "
            "echo; "
            "df -h / | awk 'NR==2{printf \"Disk: %s/%s (%s)\", $3,$2,$5}' || echo 'N/A'"
        )
        stdin, stdout, stderr = client.exec_command(commands)
        output = stdout.read().decode().strip()
        res = output.splitlines()
        client.close()
        return {
            "online": True,
            "uptime": res[0] if len(res) > 0 else "N/A",
            "cpu_model": res[1].strip() if len(res) > 1 else "N/A",
            "load": res[2] if len(res) > 2 else "N/A",
            "ram": res[3] if len(res) > 3 else "N/A",
            "disk": res[5] if len(res) > 5 else (res[4] if len(res) > 4 else "N/A")
        }
    except Exception as e:
        return {"online": False, "error": str(e)}

@dp.message(F.text == "📊 Статус серверов")
async def server_status(message: types.Message):
    servers = db.get_servers(message.from_user.id)
    if not servers:
        await message.answer("❌ Список серверов пуст.")
        return
    status_msg = await message.answer("⌛ Опрашиваю удаленные серверы по SSH...")
    final_report = []
    for s in servers:
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, get_detailed_status, s[2], s[3], s[4])
        if data["online"]:
            report = f"🖥 <b>{s[1]}</b> (<code>{s[2]}</code>)\n✅ Online | ⏱ {data['uptime']}\n📊 Load: {data['load']} | 📟 {data['ram']}\n💾 {data['disk']}"
        else:
            report = f"🖥 <b>{s[1]}</b> (<code>{s[2]}</code>)\n❌ Ошибка: {data['error']}"
        final_report.append(report)
    await status_msg.edit_text("\n\n---\n\n".join(final_report))

# --- FSM шаги ---
@dp.message(AddServer.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("🌐 Введите IP адрес:")
    await state.set_state(AddServer.waiting_for_ip)

@dp.message(AddServer.waiting_for_ip)
async def process_ip(message: types.Message, state: FSMContext):
    await state.update_data(ip=message.text)
    await message.answer("👤 Введите SSH имя пользователя:")
    await state.set_state(AddServer.waiting_for_user)

@dp.message(AddServer.waiting_for_user)
async def process_user(message: types.Message, state: FSMContext):
    await state.update_data(ssh_user=message.text)
    await message.answer("🔑 Введите SSH пароль:")
    await state.set_state(AddServer.waiting_for_password)

@dp.message(AddServer.waiting_for_password)
async def process_password(message: types.Message, state: FSMContext):
    data = await state.get_data()
    db.add_server(message.from_user.id, data['name'], data['ip'], data['ssh_user'], message.text)
    await state.clear()
    await message.answer(f"✅ Сервер <b>{data['name']}</b> сохранен!", reply_markup=get_main_keyboard())

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
