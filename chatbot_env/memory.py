import json
import os
from datetime import datetime
import re

def save_conversation(user_message, bot_response, domain="general"):
    """Save a conversation to memory"""
    if not user_message or not bot_response:
        return False
    
    conversation = {
        "user": str(user_message).strip(),
        "assistant": str(bot_response).strip(),
        "domain": domain,
        "timestamp": datetime.now().isoformat(),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "user_word_count": len(str(user_message).split()),
        "assistant_word_count": len(str(bot_response).split())
    }
    
    try:
        # Load existing conversations
        history = load_conversation_history()
        
        # Add new conversation
        history.append(conversation)
        
        # Keep only last 100 conversations to manage file size
        if len(history) > 100:
            history = history[-100:]
        
        # Save back to file
        with open('conversation_history.json', 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        print(f"Error saving conversation: {e}")
        return False

def load_conversation_history():
    """Load all conversation history"""
    try:
        if os.path.exists('conversation_history.json'):
            with open('conversation_history.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Validate data structure
                if not isinstance(data, list):
                    print("Invalid conversation history format")
                    return []
                
                # Validate each conversation
                valid_conversations = []
                for conv in data:
                    if isinstance(conv, dict) and 'user' in conv and 'assistant' in conv:
                        # Ensure required fields exist
                        if 'timestamp' not in conv:
                            conv['timestamp'] = datetime.now().isoformat()
                        if 'date' not in conv:
                            conv['date'] = datetime.now().strftime("%Y-%m-%d")
                        if 'domain' not in conv:
                            conv['domain'] = 'general'
                        
                        valid_conversations.append(conv)
                
                return valid_conversations
    except json.JSONDecodeError:
        print("Conversation history file is corrupted")
        return []
    except Exception as e:
        print(f"Error loading conversation history: {e}")
    
    return []

def get_recent_conversations(count=5):
    """Get recent conversations for context"""
    history = load_conversation_history()
    if not history:
        return []
    
    # Ensure count is valid
    count = max(1, min(count, len(history)))
    return history[-count:]

def find_relevant_conversations(query, max_results=3):
    """Find conversations related to the current query"""
    history = load_conversation_history()
    if not history or not query:
        return []
    
    relevant = []
    
    # Clean and prepare query
    query_cleaned = re.sub(r'[^\w\s]', '', query.lower())
    query_words = [word for word in query_cleaned.split() if len(word) > 2]
    
    if not query_words:
        return []
    
    for conv in history:
        # Combine user and assistant text
        conv_text = f"{conv.get('user', '')} {conv.get('assistant', '')}".lower()
        conv_cleaned = re.sub(r'[^\w\s]', '', conv_text)
        
        # Calculate relevance score
        matches = 0
        for word in query_words:
            if word in conv_cleaned:
                matches += 1
        
        # Only consider conversations with at least one significant match
        if matches > 0:
            relevance_score = matches / len(query_words)
            relevant.append((conv, relevance_score))
    
    # Sort by relevance and return top results
    relevant.sort(key=lambda x: x[1], reverse=True)
    
    # Ensure max_results is valid
    max_results = max(1, min(max_results, len(relevant)))
    return [conv[0] for conv in relevant[:max_results]]

def classify_message_domain(message):
    """Improved domain classification"""
    if not message:
        return 'general'
    
    message_lower = message.lower()
    
    # Define keywords with weights
    domain_keywords = {
        'work': {
            'keywords': ['work', 'job', 'meeting', 'deadline', 'project', 'career', 'office', 'task', 'productivity', 'business', 'colleague', 'boss', 'employee', 'salary', 'promotion'],
            'weight': 1.0
        },
        'family': {
            'keywords': ['family', 'kids', 'children', 'spouse', 'parent', 'home', 'dinner', 'birthday', 'vacation', 'husband', 'wife', 'mother', 'father', 'son', 'daughter'],
            'weight': 1.0
        },
        'entertainment': {
            'keywords': ['movie', 'music', 'game', 'book', 'netflix', 'fun', 'hobby', 'watch', 'read', 'play', 'entertainment', 'show', 'series', 'film'],
            'weight': 1.0
        },
        'health': {
            'keywords': ['health', 'exercise', 'fitness', 'doctor', 'medical', 'diet', 'workout', 'medicine', 'hospital', 'symptoms', 'sick', 'wellness'],
            'weight': 1.0
        },
        'learning': {
            'keywords': ['learn', 'study', 'education', 'course', 'skill', 'tutorial', 'how to', 'teach', 'school', 'university', 'training', 'knowledge'],
            'weight': 1.0
        },
        'finance': {
            'keywords': ['money', 'budget', 'finance', 'investment', 'savings', 'bank', 'loan', 'credit', 'debt', 'financial', 'income', 'expense'],
            'weight': 1.0
        }
    }
    
    domain_scores = {}
    
    for domain, data in domain_keywords.items():
        score = 0
        for keyword in data['keywords']:
            if keyword in message_lower:
                # Give higher score for exact matches vs partial matches
                if f" {keyword} " in f" {message_lower} ":
                    score += data['weight']
                else:
                    score += data['weight'] * 0.7  # Partial match penalty
        
        domain_scores[domain] = score
    
    # Find domain with highest score
    if domain_scores:
        max_domain = max(domain_scores.items(), key=lambda x: x[1])
        if max_domain[1] > 0:
            return max_domain[0]
    
    return 'general'

def get_conversation_stats():
    """Get basic conversation statistics"""
    history = load_conversation_history()
    
    if not history:
        return {
            'total_conversations': 0,
            'total_words': 0,
            'domains': {},
            'dates': {}
        }
    
    stats = {
        'total_conversations': len(history),
        'total_words': 0,
        'domains': {},
        'dates': {}
    }
    
    for conv in history:
        # Count words
        user_words = conv.get('user_word_count', len(conv.get('user', '').split()))
        assistant_words = conv.get('assistant_word_count', len(conv.get('assistant', '').split()))
        stats['total_words'] += user_words + assistant_words
        
        # Count domains
        domain = conv.get('domain', 'general')
        stats['domains'][domain] = stats['domains'].get(domain, 0) + 1
        
        # Count dates
        date = conv.get('date', 'unknown')
        stats['dates'][date] = stats['dates'].get(date, 0) + 1
    
    return stats