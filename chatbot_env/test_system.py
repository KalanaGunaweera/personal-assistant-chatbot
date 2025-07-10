#!/usr/bin/env python3
"""
Comprehensive test suite for Personal Assistant Chatbot
Run this before deployment to ensure everything works
"""

import os
import sys
import json
import tempfile
import shutil
from datetime import datetime
from dotenv import load_dotenv

def test_environment():
    """Test basic environment setup"""
    print("🧪 Testing Environment Setup...")
    
    # Test imports
    try:
        import streamlit
        import openai
        import pandas
        from profiles import save_user_profile, load_user_profile
        from memory import save_conversation, load_conversation_history
        from features import show_chat_statistics
        print("✅ All imports successful")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    # Test API key
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ No API key found")
        return False
    print("✅ API key found")
    
    return True

def test_profile_system():
    """Test profile save/load functionality"""
    print("\n🧪 Testing Profile System...")
    
    # Create test profile
    test_profile = {
        "name": "Test User",
        "role": "Student", 
        "communication_style": "Casual and friendly",
        "help_areas": ["Learning new things"],
        "work_hours": "Flexible schedule",
        "created_date": datetime.now().isoformat()
    }
    
    try:
        # Test save
        from profiles import save_user_profile, load_user_profile
        
        # Backup existing profile
        backup_profile = None
        if os.path.exists('user_profile.json'):
            with open('user_profile.json', 'r') as f:
                backup_profile = f.read()
        
        # Test save/load cycle
        if save_user_profile(test_profile):
            loaded_profile = load_user_profile()
            if loaded_profile and loaded_profile['name'] == 'Test User':
                print("✅ Profile save/load works")
                
                # Restore backup
                if backup_profile:
                    with open('user_profile.json', 'w') as f:
                        f.write(backup_profile)
                else:
                    os.remove('user_profile.json')
                
                return True
            else:
                print("❌ Profile load failed")
        else:
            print("❌ Profile save failed")
    except Exception as e:
        print(f"❌ Profile system error: {e}")
    
    return False

def test_memory_system():
    """Test conversation memory functionality"""
    print("\n🧪 Testing Memory System...")
    
    try:
        from memory import save_conversation, load_conversation_history, classify_message_domain
        
        # Backup existing history
        backup_history = None
        if os.path.exists('conversation_history.json'):
            with open('conversation_history.json', 'r') as f:
                backup_history = f.read()
        
        # Test conversation save
        test_user_msg = "Hello, I need help with work tasks"
        test_bot_msg = "I'd be happy to help you with work tasks!"
        
        if save_conversation(test_user_msg, test_bot_msg, "work"):
            history = load_conversation_history()
            if history and len(history) > 0:
                last_conv = history[-1]
                if (last_conv['user'] == test_user_msg and 
                    last_conv['assistant'] == test_bot_msg):
                    print("✅ Memory save/load works")
                    
                    # Test domain classification
                    domain = classify_message_domain("I have a meeting tomorrow")
                    if domain == "work":
                        print("✅ Domain classification works")
                        result = True
                    else:
                        print(f"❌ Domain classification failed: got {domain}, expected work")
                        result = False
                    
                    # Restore backup
                    if backup_history:
                        with open('conversation_history.json', 'w') as f:
                            f.write(backup_history)
                    else:
                        os.remove('conversation_history.json')
                    
                    return result
                else:
                    print("❌ Conversation data mismatch")
            else:
                print("❌ No conversations loaded")
        else:
            print("❌ Conversation save failed")
    except Exception as e:
        print(f"❌ Memory system error: {e}")
    
    return False

def test_openai_connection():
    """Test OpenAI API connection"""
    print("\n🧪 Testing OpenAI Connection...")
    
    try:
        import openai
        from dotenv import load_dotenv
        
        load_dotenv()
        api_key = os.getenv('OPENAI_API_KEY')
        
        if not api_key:
            print("❌ No API key for testing")
            return False
        
        client = openai.OpenAI(api_key=api_key)
        
        # Test simple completion
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10,
            timeout=15
        )
        
        if response and response.choices:
            print("✅ OpenAI API connection works")
            print(f"✅ Response received: {response.choices[0].message.content[:50]}...")
            return True
        else:
            print("❌ No response from OpenAI")
    except openai.AuthenticationError:
        print("❌ Invalid API key")
    except openai.RateLimitError:
        print("❌ Rate limit exceeded")
    except Exception as e:
        print(f"❌ OpenAI connection error: {e}")
    
    return False

def run_all_tests():
    """Run complete test suite"""
    print("🚀 Running Personal Assistant Test Suite")
    print("=" * 50)
    
    tests = [
        ("Environment", test_environment),
        ("Profile System", test_profile_system), 
        ("Memory System", test_memory_system),
        ("OpenAI Connection", test_openai_connection)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! Your chatbot is ready to deploy.")
        return True
    else:
        print(f"\n⚠️  {len(results) - passed} tests failed. Please fix issues before deployment.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)