# Telegram Availability Notifier

A Python script that connects to a Telegram bot to notify you when there is availability in a specific city (default: Nîmes). You can easily adjust the script to monitor any city of your choice.

# Features

Sends real-time notifications via Telegram when availability is detected.

Easy configuration to track any city. 

Lightweight and easy to run locally or on a server.

# Tech Stack

Python 3.11

python-telegram-bot library for Telegram integration

Requests/BeautifulSoup (or other scraping libraries) for checking availability

# Installation
```sql
git clone https://github.com/yourusername/telegram-availability-notifier.git
cd telegram-availability-notifier
```
# Install dependencies:

pip install requirements.txt

Configure your Telegram bot:

Create a bot via BotFather
 and get the API token.

Replace the token and chat ID in config.py (or your configuration file).

Set your city in the configuration (default: Nîmes).


# Usage

Run the script:
```sql
python Nimes.py
```
