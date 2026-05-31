# DevOps Assistant Bot 🤖

Телеграм-бот для мониторинга состояния серверов через SSH (без установки агентов).

## Функции
- 📊 Проверка статуса нескольких серверов одной кнопкой.
- ➕ Удобное добавление серверов через диалог в боте.
- 🖥 Вывод данных о CPU, RAM, Disk и Uptime.
- ⌨️ Удобная клавиатура с кнопками.

## Как запустить

1. **Клонируйте репозиторий:**
   ```bash
   git clone https://github.com/ВашЛогин/devops-assistant-bot.git
   cd devops-assistant-bot
Настройте переменные окружения:
code
Bash
cp .env.example .env
nano .env
Впишите ваш BOT_TOKEN и ADMIN_ID.
Запустите проект через Docker Compose:
code
Bash
docker-compose up -d --build
