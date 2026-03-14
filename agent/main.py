from dotenv import load_dotenv
import os
import json
import anthropic
import requests
from datetime import datetime
from strategy import RiskManager
from trust import TrustLayer

load_dotenv()

# Initialize Claude AI
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Coins to track
COINS = {
    "ethereum": "ETH",
    "bitcoin": "BTC",
    "solana": "SOL"
}

def get_live_prices() -> dict:
    """Fetch live crypto prices from CoinGecko."""
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
    """Ask Claude AI to make a trading decision."""
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=256,
        messages=[{
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
        }]
    )
    return message.content[0].text

def log_decision(entry: dict):
    """Save full pipeline result to trading log."""
    log_file = "trading_log.json"
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            log = json.load(f)
    else:
        log = []
    log.append(entry)
    with open(log_file, "w") as f:
        json.dump(log, f, indent=2)

def run_pipeline():
    print("=" * 50)
    print("🤖 SURGE AGENT — FULL PIPELINE")
    print("=" * 50 + "\n")

    # Step 1: Initialize Trust Layer & Identity
    print("📋 STEP 1: Initializing Trust Layer...")
    trust = TrustLayer()
    identity = trust.create_identity(
        agent_name="SurgeAgent-v1",
        capabilities=["spot_trading", "risk_management", "multi_asset"]
    )

    # Step 2: Initialize Risk Manager
    print("🛡️ STEP 2: Initializing Risk Manager...")
    rm = RiskManager(portfolio_value=10000)
    print(f"   Portfolio: $10,000\n")

    # Step 3: Fetch Live Prices
    print("📊 STEP 3: Fetching Live Market Data...")
    prices = get_live_prices()
    for symbol, data in prices.items():
        print(f"   {symbol}: ${data['price']:,.2f} ({data['change_24h']:.2f}%)")
    print()

    # Step 4: Analyze & Execute for each coin
    print("🔄 STEP 4: Running Agent Loop...\n")
    results = []

    for symbol, data in prices.items():
        print(f"{'─' * 40}")
        print(f"💰 Analyzing {symbol}...")

        # AI Decision
        decision = analyze_market(symbol, data['price'], data['change_24h'])
        print(f"🧠 AI Decision:\n{decision}\n")

        # Parse action
        action = "HOLD"
        for line in decision.split("\n"):
            if line.startswith("ACTION:"):
                action = line.replace("ACTION:", "").strip()

        pipeline_result = {
            "timestamp": datetime.now().isoformat(),
            "symbol": symbol,
            "price": data['price'],
            "change_24h": round(data['change_24h'], 2),
            "ai_decision": decision,
            "action": action,
            "trade_executed": False,
            "validation_score": None
        }

        # Risk Check + Trust Layer (only for BUY)
        if "BUY" in action:
            risk = rm.get_position_size(symbol, data['price'])

            if risk["approved"]:
                # Sign trade intent
                intent = trust.create_trade_intent(
                    symbol=symbol,
                    action=action,
                    price=data['price'],
                    max_usd=risk["max_usd"],
                    stop_loss=risk["stop_loss"],
                    take_profit=risk["take_profit"]
                )

                # Record reputation
                reputation = trust.record_reputation(
                    trade_intent=intent,
                    outcome="pending",
                    pnl=0.0
                )

                # Create validation artifact
                artifact = trust.create_validation_artifact(
                    intent, risk, reputation
                )

                pipeline_result["trade_executed"] = True
                pipeline_result["risk_details"] = risk
                pipeline_result["validation_score"] = artifact["validation_score"]

            else:
                print(f"❌ Risk Check Failed: {risk['reason']}\n")
        else:
            # Still create validation artifact for HOLD/SELL decisions
            intent = trust.create_trade_intent(
                symbol=symbol,
                action=action,
                price=data['price'],
                max_usd=0,
                stop_loss=0,
                take_profit=0
            )
            reputation = trust.record_reputation(
                trade_intent=intent,
                outcome="no_trade",
                pnl=0.0
            )
            artifact = trust.create_validation_artifact(
                intent, {"approved": True}, reputation
            )
            pipeline_result["validation_score"] = artifact["validation_score"]

        results.append(pipeline_result)
        log_decision(pipeline_result)

    # Step 5: Summary
    print("=" * 50)
    print("📈 PIPELINE SUMMARY")
    print("=" * 50)
    for r in results:
        trade_status = "✅ EXECUTED" if r["trade_executed"] else "⏸️ NO TRADE"
        print(f"{r['symbol']}: {r['action']} | {trade_status} | Validation: {r['validation_score']}%")
    print(f"\n🎯 Agent ID: {trust.agent_id}")
    print(f"📝 All decisions logged to trading_log.json")

if __name__ == "__main__":
    run_pipeline()