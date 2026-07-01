# Word Counter Telegram Bot 📊

A powerful Telegram bot for text analysis with support for files.

## ✨ Features

- 📝 Word count
- 🔤 Character count (with/without spaces)
- 📊 Sentence and paragraph count
- 📈 Word frequency analysis
- 📖 Reading time estimation
- 🎵 Syllable counting
- 📄 .txt file support
- 🚀 Deployed on Railway

## 🚀 Quick Start

### 1. Get Bot Token
- Message @BotFather on Telegram
- Send `/newbot`
- Name: WordCounterrrBot
- Username: @WordCounterrrBot
- Save your token

### 2. Deploy on Railway
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/your-template)

### 3. Environment Variables
Set these in Railway:
- `TELEGRAM_BOT_TOKEN` - Your bot token

## 🏃 Local Development

```bash
# Clone repository
git clone https://github.com/yourusername/word-counter-bot.git
cd word-counter-bot

# Install dependencies
pip install -r requirements.txt

# Set environment variable
export TELEGRAM_BOT_TOKEN="your_bot_token"

# Run bot
python bot.py
