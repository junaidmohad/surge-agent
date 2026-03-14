# Risk Management Module
# Controls position sizing, stop-loss, and circuit breakers

# Risk configuration
RISK_CONFIG = {
    "max_position_size": 0.10,   # Max 10% of portfolio per trade
    "stop_loss_pct": 0.05,       # Stop loss at 5% below entry
    "take_profit_pct": 0.15,     # Take profit at 15% above entry
    "max_daily_loss": 0.20,      # Circuit breaker: stop if down 20% today
    "max_leverage": 1.0,         # No leverage (1x only)
    "whitelisted_assets": ["ETH", "BTC", "SOL"]  # Only trade these
}

class RiskManager:
    def __init__(self, portfolio_value: float):
        self.portfolio_value = portfolio_value
        self.daily_loss = 0.0
        self.trades_today = []
        self.circuit_breaker_triggered = False

    def check_circuit_breaker(self) -> bool:
        """Stop all trading if daily loss exceeds limit."""
        loss_pct = self.daily_loss / self.portfolio_value
        if loss_pct >= RISK_CONFIG["max_daily_loss"]:
            self.circuit_breaker_triggered = True
            print(f"🚨 CIRCUIT BREAKER TRIGGERED! Daily loss: {loss_pct:.1%}")
            return True
        return False

    def get_position_size(self, symbol: str, price: float) -> dict:
        """Calculate safe position size for a trade."""
        
        # Check if asset is whitelisted
        if symbol not in RISK_CONFIG["whitelisted_assets"]:
            return {
                "approved": False,
                "reason": f"{symbol} is not in whitelisted assets"
            }

        # Check circuit breaker
        if self.check_circuit_breaker():
            return {
                "approved": False,
                "reason": "Circuit breaker triggered — trading halted"
            }

        # Calculate position size
        max_usd = self.portfolio_value * RISK_CONFIG["max_position_size"]
        units = max_usd / price
        stop_loss_price = price * (1 - RISK_CONFIG["stop_loss_pct"])
        take_profit_price = price * (1 + RISK_CONFIG["take_profit_pct"])

        return {
            "approved": True,
            "symbol": symbol,
            "entry_price": price,
            "max_usd": round(max_usd, 2),
            "units": round(units, 6),
            "stop_loss": round(stop_loss_price, 2),
            "take_profit": round(take_profit_price, 2),
            "leverage": RISK_CONFIG["max_leverage"]
        }

    def record_trade(self, symbol: str, pnl: float):
        """Record a completed trade and update daily loss."""
        self.trades_today.append({"symbol": symbol, "pnl": pnl})
        if pnl < 0:
            self.daily_loss += abs(pnl)
        print(f"📊 Trade recorded: {symbol} PnL: ${pnl:,.2f}")

if __name__ == "__main__":
    print("🛡️ Risk Manager Test\n")
    
    # Simulate a $10,000 portfolio
    rm = RiskManager(portfolio_value=10000)
    
    # Test position sizing for each coin
    test_prices = {"ETH": 2076.00, "BTC": 70799.00, "SOL": 86.96}
    
    for symbol, price in test_prices.items():
        print(f"{'='*40}")
        result = rm.get_position_size(symbol, price)
        if result["approved"]:
            print(f"✅ {symbol} Trade Approved:")
            print(f"   Max position: ${result['max_usd']}")
            print(f"   Units to buy: {result['units']}")
            print(f"   Stop loss:    ${result['stop_loss']}")
            print(f"   Take profit:  ${result['take_profit']}")
        else:
            print(f"❌ {symbol} Trade Rejected: {result['reason']}")
        print()