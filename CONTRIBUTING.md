# Contributing to AI Stock Analyzer

First off, thank you for considering contributing to AI Stock Analyzer! 🎉

## Code of Conduct

Be respectful and constructive in all interactions.

## How Can I Contribute?

### Reporting Bugs 🐛

Before creating bug reports, please check existing issues. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce**
- **Expected vs actual behavior**
- **Screenshots** (if applicable)
- **Environment details** (OS, Python version, etc.)

### Suggesting Features 💡

Feature requests are welcome! Please:

- **Use a clear title**
- **Provide detailed description** of the feature
- **Explain why it would be useful**
- **Include examples** if possible

### Pull Requests 🔧

1. Fork the repo and create your branch from `master`
2. If you've added code, add tests
3. Ensure the test suite passes
4. Make sure your code follows the existing style
5. Write a clear commit message
6. Update documentation if needed

## Development Setup

```bash
# Clone your fork
git clone https://github.com/your-username/ai-stock-analyzer.git
cd ai-stock-analyzer

# Create virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows Git Bash
# or
venv\Scripts\activate  # Windows CMD

# Install dependencies
pip install -r requirements.txt

# Configure API keys
cp .env.example .env
# Edit .env with your API keys

# Test setup
python test_setup.py

# Run the app
streamlit run app.py
```

## Project Structure

```
ai-stock-analyzer/
├── app.py                      # Main Streamlit app
├── config/                     # Configuration
│   ├── settings.py            # App settings
│   └── symbols.py             # Symbol definitions
├── core/                       # Core functionality
│   ├── data_manager.py        # Data orchestration
│   └── state_manager.py       # State management
├── data_sources/              # Data providers
│   ├── alpaca_provider.py     # US stocks
│   └── binance_provider.py    # Crypto
├── analysis/                   # Technical analysis
│   └── technical_indicators.py
├── llm_agent/                  # AI agent
│   ├── agent_core.py
│   ├── openrouter_provider.py
│   └── tools/                 # Agent tools
└── utils/                      # Utilities
```

## Coding Standards

- Follow PEP 8 style guide
- Use type hints where possible
- Add docstrings to functions and classes
- Keep functions focused and small
- Write descriptive variable names

## Testing

Before submitting a PR:

```bash
# Test setup
python test_setup.py

# Manual testing
streamlit run app.py
# Test all pages and features
```

## Commit Messages

Use clear, descriptive commit messages:

```bash
# Good
git commit -m "Add support for European stocks via Twelve Data API"
git commit -m "Fix WebSocket reconnection issue in BinanceProvider"

# Not so good
git commit -m "Update files"
git commit -m "Fix bug"
```

## Areas Needing Help

### High Priority
- [ ] European stocks integration (Twelve Data)
- [ ] Portfolio tracking with P&L calculations
- [ ] Real-time news integration
- [ ] Unit tests for core modules

### Medium Priority
- [ ] Backtesting framework
- [ ] More technical indicators
- [ ] Alert/notification system
- [ ] Export to CSV/Excel

### Nice to Have
- [ ] Dark mode theme
- [ ] Mobile responsiveness
- [ ] Multi-language support
- [ ] Advanced charting options

## Questions?

Feel free to:
- Open an [Issue](https://github.com/wmostert76/ai-stock-analyzer/issues)
- Start a [Discussion](https://github.com/wmostert76/ai-stock-analyzer/discussions)

Thank you for contributing! 🚀
