import os
import re
import logging
from collections import Counter
from typing import Dict, Tuple, List, Optional

import telebot
from telebot.types import Message, Document
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get bot token from environment
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not BOT_TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN not set in environment variables")
    raise ValueError("TELEGRAM_BOT_TOKEN is required")

# Initialize bot
bot = telebot.TeleBot(BOT_TOKEN, parse_mode='HTML')

# Constants
MAX_TEXT_LENGTH = 4096
MIN_TEXT_LENGTH = 3
READING_SPEED_WPM = 200


class TextAnalyzer:
    """Handles all text analysis operations"""
    
    @staticmethod
    def count_words(text: str) -> int:
        """Count total words in text"""
        return len(text.strip().split())
    
    @staticmethod
    def count_characters(text: str) -> Tuple[int, int]:
        """Count characters with and without spaces"""
        return len(text), len(text.replace(' ', ''))
    
    @staticmethod
    def count_sentences(text: str) -> int:
        """Count sentences using punctuation marks"""
        sentences = re.split(r'[.!?]+', text)
        return len([s for s in sentences if s.strip()])
    
    @staticmethod
    def count_paragraphs(text: str) -> int:
        """Count paragraphs by splitting on newlines"""
        paragraphs = text.strip().split('\n\n')
        return len([p for p in paragraphs if p.strip()])
    
    @staticmethod
    def count_unique_words(text: str) -> int:
        """Count unique words (case insensitive)"""
        words = re.findall(r'\b\w+\b', text.lower())
        return len(set(words))
    
    @staticmethod
    def count_syllables(text: str) -> int:
        """Simple syllable counter for English words"""
        words = re.findall(r'\b\w+\b', text.lower())
        total_syllables = 0
        
        for word in words:
            # Count vowel groups
            vowel_pattern = r'[aeiouy]+'
            syllables = len(re.findall(vowel_pattern, word))
            # Adjust for silent e
            if word.endswith('e') and len(word) > 2:
                syllables = max(1, syllables - 1)
            total_syllables += max(1, syllables)
        
        return total_syllables
    
    @staticmethod
    def get_word_frequency(text: str, top_n: int = 10) -> List[Tuple[str, int]]:
        """Get top N most frequent words"""
        words = re.findall(r'\b\w+\b', text.lower())
        frequency = Counter(words)
        return frequency.most_common(top_n)
    
    @staticmethod
    def get_reading_time(word_count: int) -> str:
        """Estimate reading time"""
        minutes = word_count / READING_SPEED_WPM
        if minutes < 1:
            return "Less than 1 minute"
        elif minutes < 2:
            return "~1 minute"
        else:
            return f"~{int(minutes)} minutes"
    
    @staticmethod
    def analyze(text: str) -> Dict:
        """Perform complete text analysis"""
        words = re.findall(r'\b\w+\b', text)
        word_count = TextAnalyzer.count_words(text)
        char_with_space, char_without_space = TextAnalyzer.count_characters(text)
        
        return {
            'word_count': word_count,
            'char_with_space': char_with_space,
            'char_without_space': char_without_space,
            'sentence_count': TextAnalyzer.count_sentences(text),
            'paragraph_count': TextAnalyzer.count_paragraphs(text),
            'unique_words': TextAnalyzer.count_unique_words(text),
            'avg_word_length': sum(len(w) for w in words) / len(words) if words else 0,
            'reading_time': TextAnalyzer.get_reading_time(word_count),
            'syllables': TextAnalyzer.count_syllables(text),
            'word_frequency': TextAnalyzer.get_word_frequency(text, 10)
        }


def format_analysis_results(results: Dict) -> str:
    """Format analysis results for display"""
    lines = [
        "📊 <b>Text Analysis Results</b> 📊",
        "",
        f"📝 <b>Word Count:</b> {results['word_count']:,}",
        f"🔤 <b>Characters (with spaces):</b> {results['char_with_space']:,}",
        f"🔤 <b>Characters (without spaces):</b> {results['char_without_space']:,}",
        f"📊 <b>Sentences:</b> {results['sentence_count']}",
        f"📑 <b>Paragraphs:</b> {results['paragraph_count']}",
        f"✨ <b>Unique Words:</b> {results['unique_words']:,}",
        f"🔢 <b>Average Word Length:</b> {results['avg_word_length']:.1f} characters",
        f"📖 <b>Estimated Reading Time:</b> {results['reading_time']}",
        f"🎵 <b>Syllables:</b> {results['syllables']:,}",
        "",
        "📈 <b>Top 10 Most Common Words:</b>"
    ]
    
    for i, (word, count) in enumerate(results['word_frequency'], 1):
        lines.append(f"  {i}. <b>{word}</b> → {count} times")
    
    lines.extend([
        "",
        "---",
        "💡 <b>Tips:</b>",
        "• Send a .txt file for analysis",
        "• Try longer texts for better insights",
        "• Use /help for more information"
    ])
    
    return '\n'.join(lines)


# ==================== COMMAND HANDLERS ====================

@bot.message_handler(commands=['start'])
def handle_start(message: Message):
    """Handle /start command"""
    welcome_text = """
👋 <b>Welcome to Word Counter Bot!</b>

I'm your personal text analysis assistant. Send me any text and I'll provide detailed statistics!

<b>Features:</b>
✅ Word counting
✅ Character counting
✅ Sentence & paragraph counting
✅ Word frequency analysis
✅ Reading time estimation
✅ Syllable counting
✅ File support (.txt)

<b>Quick Start:</b>
Just send me any text or .txt file!

<b>Commands:</b>
/start - Show this message
/help - Show help information
/about - About this bot
"""
    bot.reply_to(message, welcome_text)


@bot.message_handler(commands=['help'])
def handle_help(message: Message):
    """Handle /help command"""
    help_text = """
📚 <b>How to Use Word Counter Bot</b>

<b>Text Analysis:</b>
Simply send me any text message and I'll analyze it automatically.

<b>File Analysis:</b>
Send a .txt file and I'll read and analyze its contents.

<b>What I Analyze:</b>
• Total number of words
• Characters (with/without spaces)
• Number of sentences and paragraphs
• Unique word count
• Most frequently used words
• Average word length
• Reading time estimate
• Syllable count

<b>Tips:</b>
• For best results, send texts with at least 3 characters
• Maximum text length is 4000 characters
• I work best with English text

<b>Commands:</b>
/start - Welcome message
/help - This help text
/about - About this bot
"""
    bot.reply_to(message, help_text)


@bot.message_handler(commands=['about'])
def handle_about(message: Message):
    """Handle /about command"""
    about_text = """
🤖 <b>About Word Counter Bot</b>

Version: 1.0.0
Language: Python
Hosting: Railway 🚂

<b>Features:</b>
• Real-time text analysis
• File support (.txt)
• Detailed statistics
• Word frequency analysis
• Reading time estimation

<b>Technical Details:</b>
• Built with pyTelegramBotAPI
• Deployed on Railway
• Source code on GitHub

Made with ❤️ by your friendly bot developer
"""
    bot.reply_to(message, about_text)


# ==================== TEXT MESSAGE HANDLER ====================

@bot.message_handler(content_types=['text'])
def handle_text(message: Message):
    """Handle regular text messages"""
    try:
        text = message.text.strip()
        
        # Skip if it's a command (already handled)
        if text.startswith('/'):
            return
        
        # Validate text length
        if len(text) < MIN_TEXT_LENGTH:
            bot.reply_to(
                message,
                f"🤔 Please send more text (minimum {MIN_TEXT_LENGTH} characters)!"
            )
            return
        
        if len(text) > MAX_TEXT_LENGTH:
            bot.reply_to(
                message,
                f"⚠️ Text is too long! Maximum {MAX_TEXT_LENGTH} characters allowed."
            )
            return
        
        # Show typing indicator
        bot.send_chat_action(message.chat.id, 'typing')
        
        # Analyze text
        results = TextAnalyzer.analyze(text)
        formatted_results = format_analysis_results(results)
        
        bot.reply_to(message, formatted_results)
        
    except Exception as e:
        logger.error(f"Error in text handler: {e}")
        bot.reply_to(message, "❌ Oops! Something went wrong. Please try again.")


# ==================== DOCUMENT HANDLER ====================

@bot.message_handler(content_types=['document'])
def handle_document(message: Message):
    """Handle document messages"""
    try:
        doc: Document = message.document
        
        # Check if it's a text file
        if not doc.file_name or not doc.file_name.endswith('.txt'):
            bot.reply_to(message, "📄 Please send a .txt file for analysis.")
            return
        
        # Show processing status
        bot.reply_to(message, "📄 Processing your text file...")
        bot.send_chat_action(message.chat.id, 'typing')
        
        # Download file
        file_info = bot.get_file(doc.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        # Decode text
        try:
            text = downloaded_file.decode('utf-8')
        except UnicodeDecodeError:
            text = downloaded_file.decode('latin-1')
        
        # Validate text length
        if len(text) > MAX_TEXT_LENGTH * 2:
            bot.reply_to(
                message,
                f"⚠️ File is too large! Maximum file size is {MAX_TEXT_LENGTH * 2} characters."
            )
            return
        
        # Analyze text
        results = TextAnalyzer.analyze(text)
        formatted_results = format_analysis_results(results)
        
        # Add file name to response
        response = f"📄 <b>File:</b> {doc.file_name}\n\n{formatted_results}"
        bot.reply_to(message, response)
        
    except Exception as e:
        logger.error(f"Error in document handler: {e}")
        bot.reply_to(message, "❌ Error processing file. Please ensure it's a valid text file.")


# ==================== ERROR HANDLERS ====================

@bot.message_handler(content_types=['photo', 'video', 'audio', 'voice', 'sticker'])
def handle_media(message: Message):
    """Handle unsupported media types"""
    bot.reply_to(
        message,
        "📎 I can only analyze text messages and .txt files! Please send text or a text file."
    )


@bot.message_handler(func=lambda message: True)
def handle_unknown(message: Message):
    """Fallback handler for unknown message types"""
    bot.reply_to(
        message,
        "🤔 I'm not sure how to process that. Send me text or a .txt file!"
    )


# ==================== HEALTH CHECK (for Railway) ====================

import flask
from flask import Flask

app = Flask(__name__)

@app.route('/')
def health_check():
    """Health check endpoint for Railway"""
    return "Bot is running!", 200

@app.route('/health')
def health():
    """Detailed health check"""
    return {"status": "healthy", "service": "word-counter-bot"}, 200


def run_flask():
    """Run Flask app for web server"""
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)


# ==================== MAIN EXECUTION ====================

def main():
    """Main entry point"""
    logger.info("🚀 Starting Word Counter Bot...")
    
    try:
        # Remove webhook to ensure polling works
        bot.remove_webhook()
        
        # Start polling
        logger.info("✅ Bot started successfully!")
        bot.polling(none_stop=True, interval=0, timeout=20)
        
    except Exception as e:
        logger.error(f"❌ Critical error: {e}")
        raise


if __name__ == '__main__':
    # Start bot and web server in separate threads
    import threading
    from concurrent.futures import ThreadPoolExecutor
    
    with ThreadPoolExecutor(max_workers=2) as executor:
        # Start Flask server
        executor.submit(run_flask)
        # Start Telegram bot
        executor.submit(main)
