import os
import requests
from flask import Flask, request, jsonify
import time

app = Flask(__name__)

BOT_TOKEN = os.environ.get('BOT_TOKEN', '')
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def send_message(chat_id, text):
    """Send message via Telegram API"""
    url = f"{API_URL}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'Markdown'
    }
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Error sending message: {e}")

@app.route('/')
@app.route('/health')
def health():
    return "✅ Bot Running", 200

@app.route(f'/webhook/{BOT_TOKEN}', methods=['POST'])
def webhook():
    """Handle incoming Telegram messages"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'status': 'ok'}), 200
        
        message = data['message']
        chat_id = message['chat']['id']
        text = message.get('text', '')
        
        print(f"Received: {text} from {chat_id}")
        
        # Handle commands
        if text == '/start':
            send_message(chat_id, "✅ Bot is alive!\n\nSend /ping to test")
        elif text == '/ping':
            send_message(chat_id, "🏓 Pong! Bot is working.")
        elif text == '/reindex':
            send_message(chat_id, "🔄 Reindex command received.")
        elif text.startswith('/search'):
            query = text.replace('/search', '').strip()
            if query:
                send_message(chat_id, f"🔍 Searching for: {query}")
            else:
                send_message(chat_id, "Usage: /search <keyword>")
        elif text and not text.startswith('/'):
            send_message(chat_id, f"📨 {text[:100]}")
        
        return jsonify({'status': 'ok'}), 200
        
    except Exception as e:
        print(f"Webhook error: {e}")
        return jsonify({'status': 'error'}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    
    # Set webhook
    webhook_url = f"https://forwarding-bot-klzl.onrender.com/webhook/{BOT_TOKEN}"
    requests.get(f"{API_URL}/setWebhook?url={webhook_url}")
    print(f"✅ Webhook set to: {webhook_url}")
    print(f"🔥 Starting server on port {port}")
    
    app.run(host="0.0.0.0", port=port)
