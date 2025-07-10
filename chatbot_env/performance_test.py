#!/usr/bin/env python3
"""
Performance and load testing for the chatbot
"""

import time
import statistics
from memory import save_conversation, load_conversation_history
from profiles import save_user_profile, load_user_profile

def test_response_times():
    """Test API response times"""
    print("⏱️  Testing Response Times...")
    
    import openai
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    response_times = []
    test_messages = [
        "Hello",
        "What's the weather like?",
        "Help me plan my day",
        "Tell me a short joke",
        "Explain artificial intelligence"
    ]
    
    for i, message in enumerate(test_messages):
        print(f"Test {i+1}/5: {message[:20]}...")
        start_time = time.time()
        
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": message}],
                max_tokens=100,
                timeout=30
            )
            end_time = time.time()
            response_time = end_time - start_time
            response_times.append(response_time)
            print(f"  ✅ {response_time:.2f}s")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    if response_times:
        avg_time = statistics.mean(response_times)
        print(f"\n📊 Average response time: {avg_time:.2f}s")
        print(f"📊 Fastest: {min(response_times):.2f}s")
        print(f"📊 Slowest: {max(response_times):.2f}s")
        
        if avg_time < 5:
            print("✅ Performance: Excellent")
        elif avg_time < 10:
            print("⚠️  Performance: Good")
        else:
            print("❌ Performance: Slow - check internet connection")

def test_memory_performance():
    """Test memory system performance with many conversations"""
    print("\n💾 Testing Memory Performance...")
    
    # Save current state
    backup_conversations = None
    if os.path.exists('conversation_history.json'):
        with open('conversation_history.json', 'r') as f:
            backup_conversations = f.read()
    
    try:
        start_time = time.time()
        
        # Add 50 test conversations
        for i in range(50):
            save_conversation(
                f"Test user message {i}",
                f"Test assistant response {i}",
                "general"
            )
        
        # Load and measure
        load_start = time.time()
        history = load_conversation_history()
        load_time = time.time() - load_start
        
        total_time = time.time() - start_time
        
        print(f"✅ Saved 50 conversations in {total_time:.2f}s")
        print(f"✅ Loaded {len(history)} conversations in {load_time:.3f}s")
        
        if load_time < 0.1:
            print("✅ Memory Performance: Excellent")
        elif load_time < 0.5:
            print("⚠️  Memory Performance: Good")
        else:
            print("❌ Memory Performance: Slow")
        
    finally:
        # Restore backup
        if backup_conversations:
            with open('conversation_history.json', 'w') as f:
                f.write(backup_conversations)
        elif os.path.exists('conversation_history.json'):
            os.remove('conversation_history.json')

def estimate_costs():
    """Estimate usage costs"""
    print("\n💰 Cost Estimation...")
    
    # Rough token estimates for different operations
    costs = {
        "Basic chat (per message)": 0.001,
        "Profile setup (one-time)": 0.002,
        "Memory-enhanced response": 0.003,
        "Daily usage (20 messages)": 0.02,
        "Monthly usage (600 messages)": 0.60
    }
    
    print("Estimated costs (USD):")
    for operation, cost in costs.items():
        print(f"  • {operation}: ${cost:.3f}")
    
    print("\n💡 Tips to reduce costs:")
    print("  • Use shorter messages when possible")
    print("  • Set lower max_tokens for simple requests")
    print("  • Monitor usage in OpenAI dashboard")

if __name__ == "__main__":
    test_response_times()
    test_memory_performance()
    estimate_costs()