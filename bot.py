import os
import re
import logging
from collections import Counter
from flask import Flask, jsonify
import threading
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==================== FLASK APP ====================
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Word Counter Bot is running!", 200

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "service": "WordCounterrrBot",
        "version": "1.0.0"
    }), 200

# ==================== TEXT ANALYSIS ====================
def analyze_text(text):
    """Analyze text and return statistics"""
    # Clean and split
    words = re.findall(r'\b\w+\b', text.lower())
    word_count = len(words)
    
    # Basic counts
    char_with_space = len(text)
    char_without_space = len(text.replace(' ', ''))
    
    # Sentences (split by ., !, ?)
    sentences = re.split(r'[.!?]+', text)
    sentence_count = len([s for s in sentences if s.strip()])
    
    # Paragraphs
    paragraphs = [p for p in text.strip().split('\n\n') if p.strip()]
    paragraph_count = len(paragraphs)
    
    # Unique words
    unique_words = len(set(words))
    
    # Average word length
    avg_word_length = sum(len(w) for w in words) / len(words) if words else 0
    
    # Word frequency
    frequency = Counter(words)
    top_words = frequency.most_common(10)
    
    # Reading time
    reading_time = word_count / 200  # 200 words per minute
    
    return {
        'word_count': word_count,
        'char_with_space': char_with_space,
        'char_without_space': char_without_space,
        'sentence_count': sentence_count,
        'paragraph_count': paragraph_count,
        'unique_words': unique_words,
        'avg_word_length': avg_word_length,
        'top_words': top_words,
        'reading_time': reading_time
    }

def format_response(results):
    """Format results for display"""
    lines = [
        "📊 <b>Text Analysis Results</b>",
        "=" * 30,
        "",
        f"📝 <b>Words:</b> {results['word_count']:,}",
        f"🔤 <b>Characters (with spaces):</b> {results['char_with_space']:,}",
        f"🔤 <b>Characters (without spaces):</b> {results['char_without_space']:,}",
        f"📊 <b>Sentences:</b> {results['sentence_count']}",
        f"📑 <b>Paragraphs:</b> {results['paragraph_count']}",
        f"✨ <b>Unique Words:</b> {results['unique_words']:,}",
        f"🔢 <b>Avg Word Length:</b> {results['avg_word_length']:.1f} chars",
        f"⏱️ <b>Reading Time:</b> {'< 1' if results['reading_time'] < 1 else f'~{int(results["reading_time"])}'} min",
        "",
        "📈 <b>Top 10 Most Common Words:</b>"
    ]
    
    if results['top_words']:
        for i, (word, count) in enumerate(results['top_words'], 1):
            lines.append(f"  {i}. <b>{word}</b> → {count} time{'s' if count > 1 else ''}")
    else:
        lines.append("  No words found")
    
    lines.append("")
    lines.append("---")
    lines.append("💡 Send any text or .txt file for analysis!")
    
    return '\n'.join(lines)

# ==================== TELEGRAM BOT ====================
def start_telegram_bot():
    """Start the Telegram bot in a separate thread"""
    try:
        import telebot
        from telebot.types import Message
        
        BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
        
        if not BOT_TOKEN:
            logger.error("❌ TELEGRAM_BOT_TOKEN not set!")
            return
        
        bot = telebot.TeleBot(BOT_TOKEN)
        logger.info("✅ Telegram bot initialized")
        
        # ===== COMMAND HANDLERS =====
        @bot.message_handler(commands=['start', 'help'])
        def send_welcome(message):
            welcome = """
👋 <b>Welcome to Word Counter Bot!</b>

I analyze your text and give you detailed statistics!

<b>What I do:</b>
✅ Count words, characters, sentences
✅ Find most common words  
✅ Show unique words
✅ Estimate reading time
✅ Analyze .txt files

<b>How to use:</b>
Simply send me any text message!
Or send a .txt file for analysis.

<b>Commands:</b>
/start - Show this message
/help - Show this help
"""
            bot.reply_to(message, welcome, parse_mode='HTML')
        
        @bot.message_handler(content_types=['text'])
        def handle_text(message):
            try:
                text = message.text.strip()
                
                # Skip commands
                if text.startswith('/'):
                    return
                
                # Validate
                if len(text) < 3:
                    bot.reply_to(message, "🤔 Please send more text (minimum 3 characters)!")
                    return
                
                if len(text) > 4000:
                    bot.reply_to(message, "⚠️ Text too long! Maximum 4000 characters.")
                    return
                
                # Show typing
                bot.send_chat_action(message.chat.id, 'typing')
                
                # Analyze
                results = analyze_text(text)
                response = format_response(results)
                bot.reply_to(message, response, parse_mode='HTML')
                
            except Exception as e:
                logger.error(f"Text handler error: {e}")
                bot.reply_to(message, "❌ Oops! Something went wrong. Please try again.")
        
        @bot.message_handler(content_types=['document'])
        def handle_document(message):
            try:
                # Check if text file
                if not message.document.file_name or not message.document.file_name.endswith('.txt'):
                    bot.reply_to(message, "📄 Please send a .txt file!")
                    return
                
                bot.reply_to(message, "📄 Processing your file...")
                bot.send_chat_action(message.chat.id, 'typing')
                
                # Download and read file
                file_info = bot.get_file(message.document.file_id)
                downloaded = bot.download_file(file_info.file_path)
                text = downloaded.decode('utf-8')
                
                # Analyze
                results = analyze_text(text)
                response = f"📄 <b>File:</b> {message.document.file_name}\n\n{format_response(results)}"
                bot.reply_to(message, response, parse_mode='HTML')
                
            except Exception as e:
                logger.error(f"Document handler error: {e}")
                bot.reply_to(message, "❌ Error processing file. Make sure it's a valid text file.")
        
        # ===== START POLLING =====
        logger.info("🤖 Starting bot polling...")
        bot.remove_webhook()
        bot.polling(none_stop=True, interval=0, timeout=20)
        
    except Exception as e:
        logger.error(f"❌ Bot error: {e}")

# ==================== MAIN ====================
if __name__ == '__main__':
    # Get port
    port = int(os.environ.get('PORT', 8080))
    
    # Start Telegram bot in background thread
    bot_thread = threading.Thread(target=start_telegram_bot, daemon=True)
    bot_thread.start()
    logger.info("🚀 Bot thread started")
    
    # Wait a moment for bot to initialize
    time.sleep(2)
    
    # Start Flask web server
    logger.info(f"🌐 Starting web server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
