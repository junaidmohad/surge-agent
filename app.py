from flask import Flask, jsonify, render_template
from dotenv import load_dotenv
import json
import os
import sys
import threading

sys.path.append('agent')
from main import get_live_prices, analyze_market, run_pipeline

load_dotenv()

app = Flask(__name__)

# Global agent state
agent_state = {
    "agent_id": None,
    "agent_name": "SurgeAgent-v1",
    "status": "online",
    "network": "Base Sepolia (Chain ID: 84532)",
    "portfolio_value": 10000,
    "validation_score": 100.0,
    "total_decisions": 0,
    "wallet": os.getenv("WALLET_ADDRESS")
}

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/state')
def get_state():
    # Load agent identity for agent_id
    if os.path.exists('agent_identity.json'):
        with open('agent_identity.json') as f:
            identity = json.load(f)
        agent_state['agent_id'] = identity.get('identity_hash', '')[:16]

    # Load trade log to get total decisions and avg validation score
    if os.path.exists('trading_log.json'):
        with open('trading_log.json') as f:
            log = json.load(f)
        agent_state['total_decisions'] = len(log)
        if log:
            scores = [e.get('validation_score') for e in log if e.get('validation_score')]
            if scores:
                agent_state['validation_score'] = round(sum(scores) / len(scores), 1)

    return jsonify(agent_state)

@app.route('/api/market')
def get_market():
    try:
        prices = get_live_prices()
        result = {}
        for symbol, data in prices.items():
            decision_text = analyze_market(symbol, data['price'], data['change_24h'])
            action, reason, confidence = "HOLD", "", "LOW"
            for line in decision_text.split('\n'):
                if line.startswith('ACTION:'): action = line.replace('ACTION:', '').strip()
                if line.startswith('REASON:'): reason = line.replace('REASON:', '').strip()
                if line.startswith('CONFIDENCE:'): confidence = line.replace('CONFIDENCE:', '').strip()
            result[symbol] = {
                "price": data['price'],
                "change_24h": round(data['change_24h'], 2),
                "decision": {"action": action, "reason": reason, "confidence": confidence}
            }
        return jsonify({"prices": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/log')
def get_log():
    if os.path.exists('trading_log.json'):
        with open('trading_log.json') as f:
            return jsonify(json.load(f))
    return jsonify([])

@app.route('/api/run')
def run_agent():
    try:
        # Run pipeline in background thread — safe on Railway
        thread = threading.Thread(target=run_pipeline, daemon=True)
        thread.start()
        return jsonify({"status": "Agent pipeline started!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)