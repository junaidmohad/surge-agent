from dotenv import load_dotenv
import os
import anthropic
import requests

# Load environment variables
load_dotenv()

# Initialize Claude AI client
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def get_live_price(symbol: str = "ethereum") -> dict:
    """Fetch live crypto price from CoinGecko (free, no API key needed)."""
    url = f"https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": symbol,
        "vs_currencies": "usd",
        "include_24hr_change": "true"
    }
    response = requests.get(url, params=params)
    data = response.json()
    return {
        "price": data[symbol]["usd"],
        "change_24h": data[symbol]["usd_24h_change"]
    }

def analyze_market(price: float, change_24h: float) -> str:
    """Ask Claude AI to make a trading decision based on market data."""
    
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=256,
        messages=[
            {
                "role": "user",
                "content": f"""You are a trading agent. Given this market data:
                - Current ETH price: ${price}
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

if __name__ == "__main__":
    print("🤖 Surge Agent Starting...")
    print("📊 Fetching live market data...\n")
    
    # Fetch real live price
    market = get_live_price("ethereum")
    
    print(f"ETH Price: ${market['price']:,.2f}")
    print(f"24h Change: {market['change_24h']:.2f}%\n")
    
    decision = analyze_market(market['price'], market['change_24h'])
    print("🧠 AI Decision:")
    print(decision)