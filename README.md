## What the bot does

The bot allows employees to:
- Check in daily with a quick mood reflection
- Answer short weekly questions about team dynamics
- Leave anonymous comments, if needed
- Get a simple, human reply — not a robotic form

HR teams can:
- Receive structured mood reports
- View charts and weekly summaries
- Detect negative trends and support requests

## How it works

- Built in Python, using python-telegram-bot for Telegram integration
- Stores responses in a local SQLite database
- Analyzes moods using simple NLP keyword logic
- Generates visual reports and summaries
- Uses .env for secure token handling (token not visible in code)

## Project structure
- `app.py` – The entry point of the bot. It starts the bot and connects all command handlers.
- `bot.py` – Contains the main logic for handling Telegram messages, daily mood check-ins, and command responses.
- `weekly_report.py` – Handles the weekly questionnaire about team well-being and support.
- `report.py` – Responsible for generating reports based on collected data.
- `nlp_units.py` – Detects mood and emotional tone using simple keyword-based logic.
- `init_db.py` – Creates the local database used to store employee responses.
- `database.db` – The actual SQLite database that stores daily and weekly mood feedback.
- `.env` – Contains sensitive information like the Telegram bot token (this file is excluded from GitHub using `.gitignore`).
- `.gitignore` – Tells Git which files and folders to ignore (e.g. .env, .pdf, `.png`).
- `templates/` – Contains HTML templates used to generate HR reports and dashboards.
- `fonts/` – Includes a font file for multilingual PDF support (e.g. DejaVuSans for Cyrillic characters).
