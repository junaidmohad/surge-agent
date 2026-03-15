# 🤖 SurgeAgent — Trustless AI Trading Agent

> Built for the AI Trading Agents with ERC-8004 Hackathon

A fully autonomous AI trading agent that operates with **verifiable trust** using the ERC-8004 on-chain trust layer. Every decision is signed, recorded, and validated on the Base Sepolia blockchain.

## 🌐 Live Demo
**[https://web-production-dc2eb.up.railway.app](https://web-production-dc2eb.up.railway.app)**

## 🎯 What It Does
SurgeAgent is a trustless financial agent that:
- Fetches live crypto prices (ETH, BTC, SOL) from CoinGecko
- Uses Claude AI to analyze market conditions and make trading decisions
- Enforces strict risk management (position sizing, stop-loss, circuit breaker)
- Registers its identity on the ERC-8004 Identity Registry
- Signs every trade intent using EIP-712 typed data signatures
- Records reputation signals for every decision outcome
- Creates validation artifacts proving rule compliance (100% score)
- Displays everything on a live real-time dashboard

## 🏗️ Architecture
```
Live Price Data (CoinGecko API)
          ↓
AI Decision Engine (Claude AI)
          ↓
Risk Manager (Position sizing, Stop-loss, Circuit breaker)
          ↓
EIP-712 Trade Intent Signer
          ↓
ERC-8004 Trust Layer (Identity + Reputation + Validation)
          ↓
Trading Log + Live Dashboard
```

## ⚙️ Tech Stack

| Layer | Technology |
|---|---|
| AI Brain | Anthropic Claude (Haiku) |
| Blockchain | Base Sepolia Testnet (Chain ID: 84532) |
| Trust Standard | ERC-8004 (Identity, Reputation, Validation) |
| Signatures | EIP-712 typed data + EIP-155 chain binding |
| DEX Target | Aerodrome Finance on Base |
| Backend | Python + Flask |
| Blockchain SDK | web3.py + eth-account |
| Frontend | HTML/CSS/JavaScript |
| Deployment | Railway |

## 🛡️ ERC-8004 Implementation

### Identity Registry
- Agent mints an on-chain identity with name, capabilities, wallet, and risk parameters
- Identity JSON is signed with EIP-712 and hashed with keccak256
- Stored in `agent_identity.json`

### Reputation Registry
- Every trade decision (BUY/SELL/HOLD) emits a reputation signal
- Signals include outcome, PnL, and cryptographic signature
- Builds verifiable track record over time

### Validation Registry
- Every decision produces a validation artifact with 8 compliance checks:
  - ✅ Identity verified
  - ✅ Asset whitelisted
  - ✅ Position size within limit
  - ✅ Stop loss set
  - ✅ Take profit set
  - ✅ Circuit breaker checked
  - ✅ Intent signed
  - ✅ Reputation recorded
- Current validation score: **100%**

## 🔒 Risk Management

| Parameter | Value |
|---|---|
| Max Position Size | 10% of portfolio |
| Stop Loss | 5% below entry |
| Take Profit | 15% above entry |
| Max Daily Loss | 20% (circuit breaker) |
| Max Leverage | 1x (no leverage) |
| Whitelisted Assets | ETH, BTC, SOL |

## 🚀 Run Locally

### Prerequisites
- Python 3.x
- Node.js
- MetaMask wallet

### Setup
```bash
# Clone the repo
git clone https://github.com/junaidmohad/surge-agent.git
cd surge-agent

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Add your keys to .env

# Run the agent
python agent/main.py

# Run the dashboard
python app.py
# Visit http://localhost:5000
```

### Environment Variables
```
ANTHROPIC_API_KEY=your_anthropic_key
WALLET_PRIVATE_KEY=your_wallet_private_key
WALLET_ADDRESS=your_wallet_address
```

## 📁 Project Structure
```
surge-agent/
├── agent/
│   ├── main.py        # Full pipeline orchestrator
│   ├── strategy.py    # Risk manager + circuit breaker
│   └── trust.py       # ERC-8004 trust layer
├── templates/
│   └── dashboard.html # Live dashboard UI
├── app.py             # Flask web server + REST APIs
├── requirements.txt   # Python dependencies
└── Procfile           # Railway deployment config
```

## 👤 Built By
**Junaid** — Solo participant, first ever hackathon 🚀

*Built with determination, Claude AI, and a lot of debugging.*