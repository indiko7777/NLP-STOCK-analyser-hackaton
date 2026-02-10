"""Main Streamlit application for Stock Analyzer."""

import streamlit as st
import asyncio
from datetime import datetime
import pandas as pd

from core.state_manager import StateManager
from core.data_manager import DataManager
from config.symbols import WATCHLIST
from analysis import TechnicalIndicators

# Page configuration
st.set_page_config(
    page_title="Stock Analyzer Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize state manager
@st.cache_resource
def get_state_manager():
    """Get or create state manager."""
    return StateManager()

# Initialize data manager
@st.cache_resource
def get_data_manager():
    """Get or create data manager."""
    manager = DataManager()
    # Initialize in async context
    asyncio.run(manager.initialize())
    return manager

state = get_state_manager()
data_manager = get_data_manager()

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .price-card {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
        margin: 0.5rem 0;
    }
    .price-up {
        color: #00c853;
    }
    .price-down {
        color: #ff1744;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 📊 Stock Analyzer Pro")
    st.markdown("---")

    # Navigation
    page = st.radio(
        "Navigation",
        ["Dashboard", "Analysis", "Research", "Portfolio", "Settings"],
        label_visibility="collapsed"
    )

    st.markdown("---")

    # Watchlist
    st.markdown("### Watchlist")
    selected_symbol = st.selectbox(
        "Select Symbol",
        WATCHLIST,
        index=WATCHLIST.index(state.selected_symbol) if state.selected_symbol in WATCHLIST else 0
    )

    if selected_symbol != state.selected_symbol:
        state.selected_symbol = selected_symbol

    # Add to watchlist
    new_symbol = st.text_input("Add Symbol")
    if st.button("Add to Watchlist") and new_symbol:
        state.add_to_watchlist(new_symbol.upper())
        st.success(f"Added {new_symbol.upper()}")
        st.rerun()

    # Provider status
    st.markdown("---")
    st.markdown("### Connection Status")

    try:
        status = data_manager.get_provider_status()
        for provider, is_connected in status.items():
            icon = "✅" if is_connected else "❌"
            st.markdown(f"{icon} {provider.capitalize()}")
    except:
        st.markdown("⚠️ Initializing...")

# Main content area
if page == "Dashboard":
    st.markdown('<div class="main-header">📈 Market Dashboard</div>', unsafe_allow_html=True)

    # Subscribe to symbols
    try:
        asyncio.run(data_manager.subscribe_symbols([state.selected_symbol]))
    except Exception as e:
        st.error(f"Error subscribing to symbols: {e}")

    # Create columns for layout
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        st.markdown(f"### {state.selected_symbol}")

        # Get latest price
        try:
            price_data = asyncio.run(data_manager.get_latest_price(state.selected_symbol))

            if price_data:
                price = price_data.get("price", 0)
                st.markdown(f"<h1>${price:.2f}</h1>", unsafe_allow_html=True)
            else:
                st.info("Fetching price data...")
        except Exception as e:
            st.warning(f"Error fetching price: {e}")

    with col2:
        st.metric("Volume", "N/A")

    with col3:
        st.metric("24h Change", "N/A")

    # Chart section
    st.markdown("### Price Chart")

    timeframe = st.selectbox("Timeframe", ["1m", "5m", "15m", "1h", "4h", "1D"], index=5)

    try:
        # Get historical data
        df = asyncio.run(
            data_manager.get_historical_data(state.selected_symbol, timeframe, limit=100)
        )

        if df is not None and not df.empty:
            # Display chart
            st.line_chart(df["Close"])

            # Calculate and display indicators
            st.markdown("### Technical Indicators")

            indicators = TechnicalIndicators.calculate_all(df)

            # Display indicators in columns
            ind_col1, ind_col2, ind_col3, ind_col4 = st.columns(4)

            with ind_col1:
                if "rsi" in indicators and indicators["rsi"]["value"]:
                    rsi_val = indicators["rsi"]["value"]
                    st.metric("RSI (14)", f"{rsi_val:.2f}")

            with ind_col2:
                if "macd" in indicators and indicators["macd"]["macd"]:
                    macd_val = indicators["macd"]["macd"]
                    st.metric("MACD", f"{macd_val:.4f}")

            with ind_col3:
                if "bollinger" in indicators and indicators["bollinger"]["middle"]:
                    bb_mid = indicators["bollinger"]["middle"]
                    st.metric("BB Middle", f"{bb_mid:.2f}")

            with ind_col4:
                if "sma" in indicators and "sma_20" in indicators["sma"]:
                    sma_val = indicators["sma"]["sma_20"]
                    if sma_val:
                        st.metric("SMA (20)", f"{sma_val:.2f}")

            # Generate signals
            signals = TechnicalIndicators.generate_signals(indicators)

            if signals:
                st.markdown("### Trading Signals")
                signal_cols = st.columns(len(signals))

                for i, (indicator, signal) in enumerate(signals.items()):
                    with signal_cols[i]:
                        color = "🟢" if signal == "BULLISH" else "🔴" if signal == "BEARISH" else "🟡"
                        st.markdown(f"{color} **{indicator.upper()}**: {signal}")

        else:
            st.info(f"No historical data available for {state.selected_symbol}")

    except Exception as e:
        st.error(f"Error loading chart data: {e}")
        st.exception(e)

elif page == "Research":
    st.markdown('<div class="main-header">🤖 AI Research</div>', unsafe_allow_html=True)

    # Import research agent
    from llm_agent import ResearchAgent

    # Initialize agent
    @st.cache_resource
    def get_research_agent():
        """Get or create research agent."""
        try:
            return ResearchAgent(data_manager)
        except Exception as e:
            st.error(f"Failed to initialize AI agent: {e}")
            return None

    agent = get_research_agent()

    if agent:
        # Model selection
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("### Chat met de AI Analyst")
        with col2:
            available_models = ResearchAgent.get_available_models()
            selected_model = st.selectbox(
                "Model",
                available_models,
                index=0,
                label_visibility="collapsed"
            )
            if selected_model:
                agent.set_model(selected_model)

        # Display chat history
        for msg in state.get_chat_history():
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        # Chat input
        if prompt := st.chat_input("Stel een vraag over stocks, crypto, of trading..."):
            # Display user message
            with st.chat_message("user"):
                st.write(prompt)

            # Add to state
            state.add_chat_message("user", prompt)

            # Get agent response
            with st.chat_message("assistant"):
                with st.spinner("Analyseren..."):
                    try:
                        response = asyncio.run(agent.chat(prompt))
                        st.write(response)
                        state.add_chat_message("assistant", response)
                    except Exception as e:
                        error_msg = f"Error: {str(e)}"
                        st.error(error_msg)
                        state.add_chat_message("assistant", error_msg)

        # Clear chat button
        if st.button("Clear Chat History"):
            agent.clear_history()
            state.clear_chat_history()
            st.rerun()

        # Example queries
        st.markdown("---")
        st.markdown("### Voorbeeld vragen:")
        examples = [
            "Analyseer AAPL technisch",
            "Wat is de huidige prijs van BTC-USD?",
            "Bereken RSI en MACD voor TSLA",
            "Geef me een overzicht van NVDA"
        ]

        cols = st.columns(2)
        for i, example in enumerate(examples):
            with cols[i % 2]:
                if st.button(example, key=f"ex_{i}"):
                    # Add to chat
                    state.add_chat_message("user", example)
                    with st.spinner("Analyseren..."):
                        try:
                            response = asyncio.run(agent.chat(example))
                            state.add_chat_message("assistant", response)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")

    else:
        st.error("AI Research agent niet beschikbaar. Controleer je OpenRouter API key in .env")

elif page == "Analysis":
    st.markdown('<div class="main-header">📊 Deep Analysis</div>', unsafe_allow_html=True)
    st.info("Advanced technical analysis coming soon!")

elif page == "Portfolio":
    st.markdown('<div class="main-header">💼 Portfolio</div>', unsafe_allow_html=True)
    st.info("Portfolio tracking coming soon!")

elif page == "Settings":
    st.markdown('<div class="main-header">⚙️ Settings</div>', unsafe_allow_html=True)

    st.markdown("### API Configuration")
    st.info("Configure your API keys in the .env file")

    st.markdown("### Display Settings")
    auto_refresh = st.checkbox("Auto-refresh prices", value=state.auto_refresh)
    refresh_interval = st.slider("Refresh interval (seconds)", 1, 60, state.refresh_interval)

    if st.button("Save Settings"):
        st.success("Settings saved!")

# Auto-refresh
if state.auto_refresh and page == "Dashboard":
    import time
    time.sleep(state.refresh_interval)
    st.rerun()
