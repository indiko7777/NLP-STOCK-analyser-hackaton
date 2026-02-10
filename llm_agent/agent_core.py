"""Research agent core with OpenRouter integration."""

import json
from typing import List, Dict, Any, Optional
import structlog

from .openrouter_provider import OpenRouterProvider
from .tools import PriceLookupTool, TechnicalAnalysisTool, NewsSearchTool

logger = structlog.get_logger()


class ResearchAgent:
    """AI-powered research agent using OpenRouter."""

    SYSTEM_PROMPT = """You are a professional stock market research analyst with expertise in:
- Technical analysis (RSI, MACD, Bollinger Bands, Moving Averages)
- Fundamental analysis (PE ratios, revenue growth, earnings)
- Market sentiment analysis
- Portfolio management

You have access to tools to:
1. Look up current and historical prices
2. Calculate technical indicators
3. Search for financial news

When analyzing a stock:
1. First gather current price and recent price action
2. Calculate relevant technical indicators
3. Consider recent news and sentiment
4. Synthesize into actionable insights

Always cite your data sources and acknowledge uncertainty.
Provide specific price levels and percentages when possible.
Be concise but thorough in your analysis.
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
