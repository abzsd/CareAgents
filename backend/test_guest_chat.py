"""
Test script for guest chat functionality
"""
import asyncio
import os
from routes.chat import GuestChatAgent


async def test_guest_chat():
    """Test the guest chat agent"""

    # Check for API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found in environment variables")
        print("Please set it in your .env file")
        return

    print("✅ API key found")
    print(f"API key starts with: {api_key[:8]}...")

    # Create agent
    print("\n🤖 Creating guest chat agent...")
    agent = GuestChatAgent(api_key=api_key)
    print("✅ Agent created successfully")

    # Test messages
    test_messages = [
        "Hello! What is CareAgent?",
        "How can I book an appointment?",
        "What features do you offer?",
    ]

    history = []

    for i, message in enumerate(test_messages, 1):
        print(f"\n--- Test Message {i} ---")
        print(f"User: {message}")

        try:
            response = await agent.chat(message, history)
            print(f"Assistant: {response}\n")

            # Update history
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": response})

        except Exception as e:
            print(f"❌ Error: {str(e)}")
            break

    print("\n✅ Test completed successfully!")


if __name__ == "__main__":
    # Load environment variables
    import dotenv
    dotenv.load_dotenv(".env")

    # Run test
    asyncio.run(test_guest_chat())
