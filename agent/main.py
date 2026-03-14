from dotenv import load_dotenv
import os
import anthropic
import requests
import json
from datetime import datetime
from strategy import RiskManager

# Load environment variables
load_dotenv()

# Initialize Claude AI client
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Coins to track
COINS = {
    "ethereum": "ETH",
    "bitcoin": "BTC",
    "solana": "SOL"
}

def get_live_prices() -> dict:
    """Fetch live crypto prices from CoinGecko (free, no API key needed)."""
    ids = ",".join(COINS.keys())
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": ids,
        "vs_currencies": "usd",
        "include_24hr_change": "true"
    }
    response = requests.get(url, params=params)
    data = response.json()
    
    result = {}
    for coin_id, symbol in COINS.items():
        result[symbol] = {
            "price": data[coin_id]["usd"],
            "change_24h": data[coin_id]["usd_24h_change"]
        }
    return result

def analyze_market(symbol: str, price: float, change_24h: float) -> str:
    """Ask Claude AI to make a trading decision based on market data."""
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=256,
        messages=[
            {
                "role": "user",
                "content": f"""You are a trading agent. Given this market data:
                - Asset: {symbol}
                - Current price: ${price:,.2f}
                - 24h price change: {change_24h:.2f}%
                
                Should I BUY, SELL, or HOLD?
                Reply in this exact format:
                ACTION: [BUY/SELL/HOLD]
                REASON: [one sentence reason]
                CONFIDENCE: [LOW/MEDIUM/HIGH]"""
            }
        ]
    )
    return message.content[0].text

def log_decision(symbol: str, price: float, change_24h: float, decision: str):
    """Save trading decision to a log file."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "symbol": symbol,
        "price": price,
        "change_24h": round(change_24h, 2),
        "decision": decision
    }
    
    # Load existing log or start fresh
    log_file = "trading_log.json"
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            log = json.load(f)
    else:
        log = []
    
    # Append new entry and save
    log.append(log_entry)
    with open(log_file, "w") as f:
        json.dump(log, f, indent=2)
    
    print(f"📝 Decision logged at {log_entry['timestamp']}")

if __name__ == "__main__":
    print("🤖 Surge Agent Starting...")
    print("📊 Fetching live market data...\n")
    
    # Initialize risk manager with $10,000 portfolio
    rm = RiskManager(portfolio_value=10000)
    
    prices = get_live_prices()
    
    for symbol, data in prices.items():
        print(f"{'='*40}")
        print(f"💰 {symbol}: ${data['price']:,.2f} ({data['change_24h']:.2f}%)")
        
        # Get AI decision
        decision = analyze_market(symbol, data['price'], data['change_24h'])
        print("🧠 AI Decision:")
        print(decision)
        
        # If AI says BUY, check risk manager
        if "ACTION: BUY" in decision:
            risk = rm.get_position_size(symbol, data['price'])
            if risk["approved"]:
                print(f"✅ Risk Check PASSED:")
                print(f"   Max position: ${risk['max_usd']}")
                print(f"   Stop loss:    ${risk['stop_loss']}")
                print(f"   Take profit:  ${risk['take_profit']}")
            else:
                print(f"❌ Risk Check FAILED: {risk['reason']}")
        
        # Log the decision
        log_decision(symbol, data['price'], data['change_24h'], decision)
        print()