"""Research agent core with OpenRouter integration."""

import json
from typing import List, Dict, Any, Optional
import structlog

from .openrouter_provider import OpenRouterProvider
from .tools import PriceLookupTool, TechnicalAnalysisTool, NewsSearchTool

logger = structlog.get_logger()


class ResearchAgent:
    """AI-powered research agent using OpenRouter."""

    SYSTEM_PROMPT = """You are a Senior Quantitative Equity Strategist and Technical Portfolio Manager. Your objective is to provide institutional-grade market intelligence by synthesizing raw data into high-conviction, risk-adjusted analysis.

I. Analytical Framework & Methodology
You must approach every stock analysis through a multi-factor lens, following this hierarchical sequence:

Macro-Contextual Layer: Identify the current market regime (e.g., inflationary, risk-off, sector rotation). How does the specific sector (S&P 500, Nasdaq-100, etc.) influence the individual ticker?

Quantitative Technical Layer: * Trend: Analyze SMA/EMA crossovers (50-day vs. 200-day) to determine primary and secondary trends.

Momentum: Use RSI (identifying divergence, not just overbought/oversold) and MACD histogram shifts.

Volatility: Utilize Bollinger Bands or ATR (Average True Range) to define "noise" vs. "breakout."

Fundamental & Valuation Layer: * Assess quality through P/E, P/S, and EV/EBITDA relative to 5-year historical means and industry peers.

Analyze the "Earnings Quality"—is growth driven by revenue expansion or just share buybacks?

Sentiment & Catalyst Layer: Scrutinize recent 8-K filings, earnings call transcripts, and news sentiment. Identify "unpriced" catalysts (e.g., upcoming FDA approvals, legal rulings, or product launches).

II. Execution Constraints & Output Style
Precision: Never use vague terms like "the stock went up a lot." Use "The security appreciated $14.20 (5.4%) on 2x relative volume."

The "Bear Case" Requirement: Every bullish analysis must include a "Thesis Invalidation Point"—a specific price level or fundamental event that would prove your analysis wrong.

Data Integrity: Distinguish between trailing data (LTM) and forward-looking estimates (NTM). Always cite timestamps for price data.

Formatting: Use bold headers, bulleted data points, and tables for comparative metrics to ensure high scannability.

III. Risk Management Guardrails
No Financial Advice: Include a standard disclaimer that you provide "informational analysis, not personalized financial advice."

Uncertainty Quantification: Use probabilistic language (e.g., "There is a 60% historical probability of mean reversion at these RSI levels").

No Penny Stocks: Unless specifically requested, prioritize mid-to-large-cap equities with sufficient liquidity to avoid "pump and dump" signal noise.

IV. Structured Response Template
To ensure consistency, structure your reports as follows:

Executive Summary: (The "Bottom Line Up Front")

Technical Dashboard: (Current Price, Support/Resistance levels, Momentum score)

Fundamental Health: (Valuation vs. Peers, Growth trajectory)

Catalysts & Risks: (What moves the needle next?)

Actionable Levels: (Entry zones, Stop-loss suggestions, and Price targets)
"""

    def __init__(self, data_manager, api_key: Optional[str] = None, model: Optional[str] = None):
        """Initialize research agent."""
        self.llm = OpenRouterProvider(api_key=api_key, model=model)
        self.data_manager = data_manager

        # Initialize tools
        self.tools = {
            "price_lookup": PriceLookupTool(data_manager),
            "technical_analysis": TechnicalAnalysisTool(data_manager),
            "news_search": NewsSearchTool()
        }

        self.conversation_history: List[Dict[str, str]] = []

    def _get_function_schemas(self) -> List[Dict[str, Any]]:
        """Get all tool function schemas."""
        return [tool.get_function_schema() for tool in self.tools.values()]

    async def chat(self, user_message: str, stream: bool = False) -> str:
        """Send a message and get a response."""
        try:
            # Add user message to history
            self.conversation_history.append({
                "role": "user",
                "content": user_message
            })

            # Prepare messages with system prompt
            messages = [
                {"role": "system", "content": self.SYSTEM_PROMPT}
            ] + self.conversation_history

            # Get function schemas
            functions = self._get_function_schemas()

            # Make LLM call with function calling
            response = await self.llm.function_call(
                messages=messages,
                functions=functions,
                temperature=0.7
            )

            # Check if LLM wants to call a function
            choice = response["choices"][0]
            message = choice["message"]

            # Handle function calls
            if "function_call" in message:
                function_call = message["function_call"]
                function_name = function_call["name"]
                function_args = json.loads(function_call["arguments"])

                logger.info(f"Agent calling function: {function_name} with args: {function_args}")

                # Execute the function
                if function_name in self.tools:
                    tool = self.tools[function_name]
                    function_result = await tool.execute(**function_args)

                    # Add function call and result to conversation
                    self.conversation_history.append({
                        "role": "assistant",
                        "content": None,
                        "function_call": function_call
                    })

                    self.conversation_history.append({
                        "role": "function",
                        "name": function_name,
                        "content": json.dumps(function_result)
                    })

                    # Get final response from LLM
                    messages = [
                        {"role": "system", "content": self.SYSTEM_PROMPT}
                    ] + self.conversation_history

                    final_response = await self.llm.chat_completion(
                        messages=messages,
                        temperature=0.7
                    )

                    assistant_message = final_response["choices"][0]["message"]["content"]

                else:
                    assistant_message = f"Unknown function: {function_name}"

            else:
                # No function call, just get the content
                assistant_message = message["content"]

            # Add assistant response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })

            return assistant_message

        except Exception as e:
            logger.error(f"Agent error: {e}")
            return f"I encountered an error: {str(e)}"

    async def chat_stream(self, user_message: str):
        """Send a message and get a streaming response."""
        try:
            # Add user message to history
            self.conversation_history.append({
                "role": "user",
                "content": user_message
            })

            # Prepare messages with system prompt
            messages = [
                {"role": "system", "content": self.SYSTEM_PROMPT}
            ] + self.conversation_history

            # Stream response
            full_response = ""
            async for chunk in self.llm.chat_completion_stream(messages=messages):
                full_response += chunk
                yield chunk

            # Add to history
            self.conversation_history.append({
                "role": "assistant",
                "content": full_response
            })

        except Exception as e:
            logger.error(f"Agent streaming error: {e}")
            yield f"Error: {str(e)}"

    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []

    def set_model(self, model: str):
        """Change the LLM model."""
        self.llm.set_model(model)

    @staticmethod
    def get_available_models() -> List[str]:
        """Get available models."""
        return OpenRouterProvider.get_available_models()
