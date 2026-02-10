# 📈 AI Stock Analyzer

AI-powered stock market analysis tool using LLM agents, technical indicators, and real-time market data. Built with Python and Streamlit for interactive financial analysis and trading insights.

## 🎯 What It Does

An intelligent stock analysis platform that combines:
- **LLM-powered insights** - AI agent analyzes market data and provides trading recommendations
- **Technical analysis** - Automated calculation of key indicators (RSI, MACD, Moving Averages)
- **Real-time data** - Live market data from Alpaca and Binance
- **News integration** - Sentiment analysis from financial news sources
- **Interactive dashboard** - Streamlit-based UI for visualization

## ✨ Key Features

### AI Agent Core
- **OpenRouter LLM integration** - Powered by advanced language models
- **Multi-tool agent** - Combines price lookup, technical analysis, and news search
- **Context-aware responses** - Understands market conditions and historical patterns
- **Natural language queries** - Ask questions like "Should I buy AAPL?" and get detailed analysis

### Technical Analysis
- **Price indicators** - SMA, EMA, Bollinger Bands
- **Momentum indicators** - RSI, MACD, Stochastic Oscillator  
- **Volume analysis** - OBV, volume trends
- **Pattern recognition** - Identify support/resistance levels

### Data Sources
- **Alpaca API** - Stock and crypto market data
- **Binance API** - Cryptocurrency prices and orderbook data
- **News APIs** - Real-time financial news aggregation
- **Historical data** - Backtesting capabilities with DuckDB storage

### Dashboard Features
- **Real-time charts** - Candlestick, line, and area charts
- **Multi-symbol tracking** - Monitor multiple stocks simultaneously
- **Custom alerts** - Price and indicator-based notifications
- **Export capabilities** - Save analysis results and reports

## 🛠️ Tech Stack

**Backend:**
- Python 3.8+
- Streamlit - Interactive web framework
- DuckDB - Embedded analytics database
- Pandas/NumPy - Data manipulation

**AI/ML:**
- OpenRouter API - LLM access
- Custom agent framework - Tool-based AI reasoning
- Technical indicators - TA-Lib or pandas-ta

**Data Providers:**
- Alpaca Markets API
- Binance API
- News APIs (configurable)

**DevOps:**
- Environment-based configuration
- Logging system
- State management
- Error handling

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- API keys for:
  - OpenRouter (LLM)
  - Alpaca Markets (stock data)
  - Binance (optional, for crypto)

### Installation

```bash
# Clone the repository
git clone https://github.com/indiko7777/ai-stock-analyzer.git
cd ai-stock-analyzer

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

1. **Copy environment template:**
```bash
cp .env.example .env
```

2. **Add your API keys to `.env`:**
```env
# LLM Provider
OPENROUTER_API_KEY=your_openrouter_key_here

# Data Providers
ALPACA_API_KEY=your_alpaca_key_here
ALPACA_SECRET_KEY=your_alpaca_secret_here
BINANCE_API_KEY=your_binance_key_here (optional)

# Optional: News API
NEWS_API_KEY=your_news_api_key_here
```

### Run the Application

**Windows:**
```bash
run.bat
# or
streamlit run app.py
```

**Mac/Linux:**
```bash
./run.sh
# or
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 📊 Usage Examples

### Basic Stock Analysis
1. Enter a stock symbol (e.g., AAPL, TSLA, NVDA)
2. Select timeframe and indicators
3. Ask the AI: "What's the technical outlook for this stock?"
4. Review AI insights and technical indicators

### Advanced Queries
- "Compare AAPL and MSFT performance over the last month"
- "What are the key support and resistance levels for TSLA?"
- "Should I buy or sell based on current RSI and MACD signals?"
- "What's the market sentiment for tech stocks today?"

### Crypto Analysis
1. Switch to crypto mode
2. Select cryptocurrency pair (BTC/USDT, ETH/USDT)
3. Analyze orderbook depth and volume trends
4. Get AI trading recommendations

## 📁 Project Structure

```
ai-stock-analyzer/
│
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
│
├── analysis/                   # Technical analysis modules
│   └── technical_indicators.py
│
├── llm_agent/                  # AI agent core
│   ├── agent_core.py          # Main agent logic
│   ├── openrouter_provider.py # LLM provider integration
│   └── tools/                 # Agent tools
│       ├── price_lookup.py
│       ├── technical_analysis.py
│       └── news_search.py
│
├── data_sources/              # Market data providers
│   ├── base.py
│   ├── alpaca_provider.py
│   └── binance_provider.py
│
├── core/                      # Core functionality
│   ├── data_manager.py       # Data handling
│   └── state_manager.py      # State management
│
├── config/                    # Configuration
│   ├── settings.py
│   └── symbols.py            # Stock/crypto symbols
│
├── utils/                     # Utilities
│   └── logging_config.py
│
└── data/                      # Local data storage
```

## 🧠 How the AI Agent Works

The AI agent uses a **tool-based reasoning framework**:

1. **User query** → Natural language input
2. **Intent recognition** → Agent determines required tools
3. **Tool execution** → Fetch data, run analysis, search news
4. **Context synthesis** → Combine results from multiple sources
5. **Response generation** → LLM creates comprehensive analysis
6. **Action recommendation** → Buy/sell/hold with reasoning

**Tools available to the agent:**
- `get_current_price()` - Real-time price data
- `calculate_indicators()` - Technical analysis
- `search_news()` - Market news and sentiment
- `get_historical_data()` - Price history for backtesting
- `compare_stocks()` - Multi-symbol comparison

## 💡 Use Cases

**For Traders:**
- Quick technical analysis without manual calculations
- AI-powered entry/exit point suggestions
- News sentiment integration

**For Investors:**
- Long-term trend analysis
- Fundamental + technical combined insights
- Portfolio diversification recommendations

**For Learning:**
- Understand how technical indicators work
- See AI reasoning process
- Experiment with different strategies

## 🔮 Future Enhancements

- [ ] Portfolio tracking and optimization
- [ ] Backtesting framework
- [ ] Custom indicator builder
- [ ] Multi-timeframe analysis
- [ ] Social sentiment analysis (Twitter, Reddit)
- [ ] Automated trading signals
- [ ] Mobile-responsive design
- [ ] Multi-user support with authentication

## 📝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

**This tool is for educational and research purposes only.** 

- Not financial advice
- Past performance doesn't guarantee future results
- Always do your own research (DYOR)
- Consult a licensed financial advisor before making investment decisions
- Trading involves risk of loss

## 👨‍💻 Developer

**indiko7777**

This project demonstrates:
- AI agent development with LLM integration
- Financial data analysis and visualization
- Real-time API integrations
- Full-stack Python development
- Production-ready application architecture

## 🙏 Acknowledgments

- Original project structure inspired by modern AI agent frameworks
- Technical analysis formulas from industry standards
- LLM integration via OpenRouter
- Data providers: Alpaca Markets, Binance

---

*Built with Python, Streamlit, and AI to democratize financial analysis* 📊🤖
