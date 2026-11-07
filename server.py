```python
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(name)
CORS(app)

# Simple in-memory store for demo; use SQLite/Postgres for production
data_store = []

@app.route('/api/report/add', methods=['POST'])
def add_report():
data = request.json
data_store.append(data)
return jsonify({"status": "ok", "count": len(data)}), 200

@app.route('/api/reports', methods=['GET'])
def get_reports():
return jsonify(data_store)

if name == 'main':
app.run(host='0.0.0.0', port=5000)
```

NoTrack AI — https://notrack.ai/
