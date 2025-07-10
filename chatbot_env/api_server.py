from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Import your existing modules
from profiles import save_user_profile, load_user_profile
from memory import save_conversation, get_recent_conversations, find_relevant_conversations, classify_message_domain
import openai

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

def get_smart_response(message, profile=None):
    """Your existing smart response function"""
    try:
        client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Get conversation context
        relevant_conversations = find_relevant_conversations(message, max_results=2)
        recent_conversations = get_recent_conversations(3)
        
        # Build memory context
        memory_context = ""
        if relevant_conversations:
            memory_context += "Previous relevant conversations:\n"
            for conv in relevant_conversations:
                memory_context += f"- You previously discussed: '{conv['user'][:60]}...'\n"
        
        if recent_conversations:
            memory_context += "\nRecent context:\n"
            for conv in recent_conversations[-2:]:
                memory_context += f"- Recent: {conv['user'][:40]}... -> {conv['assistant'][:40]}...\n"
        
        # Build personalized system prompt
        if profile:
            system_prompt = f"""You are a personalized assistant for {profile['name']}.
            
About them:
- Role: {profile['role']}
- Work/Study: {profile['work_area']}
- Communication style: {profile['communication_style']}
- Work schedule: {profile['work_hours']}
- Interests: {profile['interests']}
- Family: {profile.get('family_info', 'Not specified')}
- Areas they want help with: {', '.join(profile['help_areas'])}

{memory_context}

Respond in a {profile['communication_style'].lower()} way, considering their background and previous conversations.
Reference their interests and past discussions when relevant."""
        else:
            system_prompt = f"You are a helpful personal assistant.\n{memory_context}"
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            max_tokens=250,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        message = data.get('message', '')
        profile = data.get('profile')
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Get AI response
        response = get_smart_response(message, profile)
        
        # Classify domain
        domain = classify_message_domain(message)
        
        # Save conversation
        save_conversation(message, response, domain)
        
        return jsonify({
            'response': response,
            'domain': domain,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/profile', methods=['GET', 'POST'])
def profile():
    if request.method == 'GET':
        profile = load_user_profile()
        return jsonify(profile)
    
    elif request.method == 'POST':
        try:
            profile_data = request.json
            success = save_user_profile(profile_data)
            
            if success:
                return jsonify({'success': True})
            else:
                return jsonify({'error': 'Failed to save profile'}), 500
                
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/api/conversations', methods=['GET'])
def conversations():
    try:
        from memory import load_conversation_history
        history = load_conversation_history()
        return jsonify(history)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def stats():
    try:
        from memory import get_conversation_stats
        stats = get_conversation_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)