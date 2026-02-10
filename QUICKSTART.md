# 🚀 Quick Start Guide

## ✅ Setup Complete!

Je virtual environment is klaar met alle dependencies geïnstalleerd.

## 📝 Stap 1: Configureer API Keys

1. **Kopieer het environment bestand:**
   ```bash
   cp .env.example .env
   ```

2. **Bewerk `.env` en voeg je API keys toe:**

   **Minimum vereist (GRATIS!):**
   ```env
   # OpenRouter (gratis model: Xiaomi Mimo v2 Flash)
   OPENROUTER_API_KEY=your_key_here

   # Alpaca (gratis Paper Trading API)
   ALPACA_API_KEY=your_key_here
   ALPACA_SECRET_KEY=your_secret_here
   ```

   **Optioneel:**
   ```env
   TWELVE_DATA_API_KEY=your_key_here
   ALPHA_VANTAGE_API_KEY=your_key_here
   ```

### 🔑 Waar krijg je de keys?

#### OpenRouter (GRATIS met Xiaomi model)
1. Ga naar: https://openrouter.ai/
2. Maak account aan
3. Ga naar Settings → API Keys
4. Genereer nieuwe key
5. **GEEN credits nodig** - Xiaomi Mimo v2 Flash is gratis!

#### Alpaca (GRATIS Paper Trading)
1. Ga naar: https://alpaca.markets/
2. Sign up (gratis)
3. Ga naar Paper Trading
4. Kopieer API Key en Secret Key
5. Volledig GRATIS voor real-time data!

## 🎮 Stap 2: Start de Applicatie

### Windows (CMD/PowerShell):
```bash
venv\Scripts\activate
streamlit run app.py
```

### Windows (Git Bash):
```bash
source venv/Scripts/activate
streamlit run app.py
```

### Linux/Mac:
```bash
source venv/bin/activate
streamlit run app.py
```

De app opent automatisch in je browser op: **http://localhost:8501**

## 🎯 Stap 3: Test de Setup (Optioneel)

Test of alles werkt:

```bash
source venv/Scripts/activate  # Git Bash
# OF
venv\Scripts\activate        # CMD/PowerShell

python test_setup.py
```

## 💡 Features om te proberen

### 1. Dashboard
- Selecteer een symbol (AAPL, BTC-USD, etc.)
- Bekijk real-time prijzen
- Analyseer technische indicatoren
- Check trading signals

### 2. AI Research
Ga naar de Research tab en vraag:
- "Analyseer AAPL technisch"
- "Wat is de huidige prijs van BTC-USD?"
- "Bereken RSI en MACD voor TSLA"
- "Geef me een overzicht van NVDA"

### 3. Watchlist
- Voeg symbols toe via de sidebar
- Ondersteunde formats:
  - US stocks: `AAPL`, `MSFT`, `TSLA`
  - Crypto: `BTC-USD`, `ETH-USD`

## ⚙️ Instellingen

In de Settings tab kun je aanpassen:
- Auto-refresh interval
- Refresh frequentie
- Model selectie (Xiaomi is gratis!)

## 🛑 Applicatie Stoppen

Druk op `Ctrl+C` in je terminal.

## 🔄 Later opnieuw starten

```bash
# 1. Activeer venv
source venv/Scripts/activate  # Git Bash
# OF
venv\Scripts\activate        # CMD/PowerShell

# 2. Start app
streamlit run app.py
```

## 🆘 Troubleshooting

### "ModuleNotFoundError"
Zorg dat de venv actief is:
```bash
source venv/Scripts/activate  # Git Bash
venv\Scripts\activate        # Windows CMD
```

### "API keys not configured"
Controleer dat `.env` bestaat en de juiste keys bevat.

### "No data available"
- Check internetverbinding
- Verificeer API keys zijn correct
- Probeer een ander symbol

### WebSocket errors
- Normaal bij eerste verbinding
- Auto-reconnect is ingebouwd
- Wacht een paar seconden

## 📚 Meer Info

Zie `README.md` voor uitgebreide documentatie.

## 🎉 Klaar!

Je Stock Analyzer is klaar voor gebruik! 🚀📈
