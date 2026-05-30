import asyncio
import os
import requests  # Мы используем requests, как вы просили
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

TOKEN =os.getenv ("BOT_TOKEN")
API_URL = "http://191.44.108.127:8000/status"

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

@dp.message(Command("status"))
async def cmd_status(message: types.Message):
    try:
        # Делаем запрос к нашему FastAPI
        response = requests.get(API_URL)
        data = response.json()

        # Форматируем текст на основе полученного JSON
        text = (
            f"🖥 <b>Статус через FastAPI:</b>\n\n"
            f"<b>Система:</b> {data['system']} {data['release']}\n"
            f"<b>Аптайм:</b> {data['uptime']}\n\n"
            f"<b>CPU:</b> <code>{data['cpu_usage']}%</code> (ядер: {data['cpu_count']})\n"
            f"<b>RAM:</b> <code>{data['ram']['used']}</code> / <code>{data['ram']['total']}</code> ({data['ram']['percent']}%)\n"
            f"<b>Disk:</b> <code>{data['disk']['used']}</code> / <code>{data['disk']['total']}</code> ({data['disk']['percent']}%)"
        )
    except Exception as e:
        text = f"❌ Ошибка связи с API: {e}"

    await message.answer(text)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
