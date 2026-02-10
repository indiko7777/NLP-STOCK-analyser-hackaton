"""Test script to verify Stock Analyzer setup."""

import asyncio
from config.settings import settings


def test_config():
    """Test configuration."""
    print("Testing configuration...")
    print(f"✓ Base directory: {settings.base_dir}")
    print(f"✓ Data directory: {settings.data_dir}")
    print(f"✓ Debug mode: {settings.debug}")
    print()


def test_api_keys():
    """Test API keys."""
    print("Checking API keys...")

    keys_status = {
        "OpenRouter": bool(settings.api_keys.openrouter),
        "Alpaca": bool(settings.api_keys.alpaca_key and settings.api_keys.alpaca_secret),
        "Twelve Data": bool(settings.api_keys.twelve_data),
        "Alpha Vantage": bool(settings.api_keys.alpha_vantage),
    }

    for name, configured in keys_status.items():
        status = "✓" if configured else "✗"
        print(f"{status} {name}: {'Configured' if configured else 'Not configured'}")

    print()
    return all([keys_status["OpenRouter"], keys_status["Alpaca"]])


async def test_data_providers():
    """Test data providers."""
    print("Testing data providers...")

    try:
        from core.data_manager import DataManager

        manager = DataManager()
        await manager.initialize()

        status = manager.get_provider_status()

        for provider, is_connected in status.items():
            icon = "✓" if is_connected else "✗"
            print(f"{icon} {provider.capitalize()}: {'Connected' if is_connected else 'Failed'}")

        await manager.shutdown()
        print()
        return any(status.values())

    except Exception as e:
        print(f"✗ Error initializing data providers: {e}")
        print()
        return False


async def test_llm_agent():
    """Test LLM agent."""
    print("Testing LLM agent...")

    try:
        from llm_agent import ResearchAgent
        from core.data_manager import DataManager

        manager = DataManager()
        await manager.initialize()

        agent = ResearchAgent(manager)
        print("✓ LLM agent initialized successfully")

        # Test available models
        models = ResearchAgent.get_available_models()
        print(f"✓ Available models: {len(models)}")

        await manager.shutdown()
        print()
        return True

    except Exception as e:
        print(f"✗ Error initializing LLM agent: {e}")
        print()
        return False


async def main():
    """Run all tests."""
    print("=" * 50)
    print("Stock Analyzer Pro - Setup Test")
    print("=" * 50)
    print()

    # Test configuration
    test_config()

    # Test API keys
    keys_ok = test_api_keys()

    # Test data providers
    providers_ok = await test_data_providers()

    # Test LLM agent
    llm_ok = await test_llm_agent()

    # Summary
    print("=" * 50)
    print("Summary")
    print("=" * 50)

    if keys_ok and providers_ok and llm_ok:
        print("✓ All tests passed! Ready to run Stock Analyzer.")
        print()
        print("Run the app with: streamlit run app.py")
    else:
        print("✗ Some tests failed. Please check the errors above.")
        print()
        if not keys_ok:
            print("  - Configure your API keys in .env file")
        if not providers_ok:
            print("  - Check your internet connection and API keys")
        if not llm_ok:
            print("  - Verify OpenRouter API key is correct")

    print()


if __name__ == "__main__":
    asyncio.run(main())
