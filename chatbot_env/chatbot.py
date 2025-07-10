import streamlit as st
import openai
import os
from datetime import datetime
from dotenv import load_dotenv
from profiles import show_profile_setup, load_user_profile
from memory import save_conversation, get_recent_conversations, find_relevant_conversations, classify_message_domain
from features import show_chat_statistics, export_data

# Load environment variables
load_dotenv()

# Configure the page
st.set_page_config(
    page_title="Personal Assistant Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

def check_openai_connection():
    """Check if OpenAI API is accessible"""
    try:
        client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=5
        )
        return True
    except Exception as e:
        return False, str(e)

def get_smart_response(message, profile=None):
    """Get a smart, personalized response with memory"""
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

def main():
    # Custom CSS for better UI
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #4CAF50, #45a049);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 1rem;
    }
    .status-good { color: #4CAF50; font-weight: bold; }
    .status-bad { color: #f44336; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("🎛 Personal Assistant")
    page = st.sidebar.selectbox("Navigate to:", [
        "💬 Chat Assistant",
        "👤 My Profile", 
        "📊 Statistics",
        "📥 Export Data"
    ])
    
    # Check system status
    api_key_exists = bool(os.getenv('OPENAI_API_KEY'))
    openai_connected = False
    profile = load_user_profile()
    
    # Sidebar status
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔧 System Status")
    
    if api_key_exists:
        connection_result = check_openai_connection()
        if connection_result == True:
            openai_connected = True
            st.sidebar.markdown('<p class="status-good">✅ OpenAI Ready</p>', unsafe_allow_html=True)
        else:
            st.sidebar.markdown('<p class="status-bad">❌ OpenAI Connection Failed</p>', unsafe_allow_html=True)
    else:
        st.sidebar.markdown('<p class="status-bad">❌ No API Key</p>', unsafe_allow_html=True)
    
    if profile:
        st.sidebar.markdown('<p class="status-good">✅ Profile Set</p>', unsafe_allow_html=True)
        st.sidebar.markdown(f"**👋 {profile['name']}**")
    else:
        st.sidebar.markdown('<p class="status-bad">⚠️ No Profile</p>', unsafe_allow_html=True)
    
    # Quick stats in sidebar
    if page != "📊 Statistics":
        from memory import load_conversation_history
        history = load_conversation_history()
        if history:
            st.sidebar.markdown("---")
            st.sidebar.markdown("### 📈 Quick Stats")
            st.sidebar.metric("Conversations", len(history))
            domains = {}
            for conv in history:
                domain = conv.get('domain', 'general') 
                domains[domain] = domains.get(domain, 0) + 1
            if domains:
                top_domain = max(domains.items(), key=lambda x: x[1])
                st.sidebar.metric("Top Topic", top_domain[0].title())
    
    # Page routing
    if page == "👤 My Profile":
        show_profile_setup()
    elif page == "📊 Statistics":
        show_chat_statistics()
    elif page == "📥 Export Data":
        export_data()
    else:  # Chat page
        # Header
        st.markdown('<div class="main-header"><h1>🤖 Personal Assistant Chatbot</h1><p>Smart • Personalized • Private</p></div>', unsafe_allow_html=True)
        
        # Check if system is ready
        if not api_key_exists:
            st.error("❌ **OpenAI API key not found!**")
            st.info("Please check your .env file contains: OPENAI_API_KEY=your_key_here")
            return
        
        if not openai_connected:
            st.error("❌ **Cannot connect to OpenAI!**") 
            st.info("Please check your API key and internet connection.")
            return
        
        # Create main layout
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Welcome message
            if profile:
                st.success(f"👋 Welcome back, {profile['name']}! I remember our previous conversations and I'm ready to help.")
            else:
                st.info("👋 Welcome! I'm your personal AI assistant. Set up your profile for personalized responses!")
            
            # Initialize chat
            if "messages" not in st.session_state:
                st.session_state.messages = []
            
            # Display chat history
            chat_container = st.container()
            with chat_container:
                if not st.session_state.messages:
                    st.markdown("💡 **Try asking me about:**")
                    st.markdown("• Help me plan my day")
                    st.markdown("• What should I do for entertainment?")
                    st.markdown("• Give me work productivity tips")
                    st.markdown("• How can I improve my health?")
                
                for i, message in enumerate(st.session_state.messages):
                    if message["role"] == "user":
                        st.markdown(f"**🧑 You:** {message['content']}")
                    else:
                        st.markdown(f"**🤖 Assistant:** {message['content']}")
                    
                    if i < len(st.session_state.messages) - 1:
                        st.markdown("---")
            
            # Chat input
            user_input = st.text_input("💬 Type your message here:",
                                     placeholder="Ask me anything...")
            
            # Buttons
            col_send, col_clear = st.columns([2, 1])
            with col_send:
                send_button = st.button("📤 Send Message", use_container_width=True, type="primary")
            with col_clear:
                clear_button = st.button("🗑 Clear", use_container_width=True)
            
            # Handle send
            if send_button and user_input.strip():
                # Add user message
                st.session_state.messages.append({"role": "user", "content": user_input})
                
                # Get smart response
                with st.spinner("🤔 AI is thinking..."):
                    bot_response = get_smart_response(user_input, profile)
                
                # Add bot response
                st.session_state.messages.append({"role": "assistant", "content": bot_response})
                
                # Save to memory
                domain = classify_message_domain(user_input)
                save_conversation(user_input, bot_response, domain)
                
                # Refresh
                st.rerun()
            
            # Handle clear
            if clear_button:
                st.session_state.messages = []
                st.rerun()
        
        with col2:
            st.markdown("### 💡 Smart Features")
            st.markdown("✅ **Personalized responses**")
            st.markdown("✅ **Remembers conversations**")
            st.markdown("✅ **Domain-aware**")
            st.markdown("✅ **Usage analytics**")
            st.markdown("✅ **Data export**")
            
            if profile:
                st.markdown("---")
                st.markdown("### 🎯 Your Setup")
                st.markdown(f"**Role:** {profile['role']}")
                st.markdown(f"**Style:** {profile['communication_style']}")
                interests_preview = profile['interests'][:50] + "..." if len(profile['interests']) > 50 else profile['interests']
                st.markdown(f"**Interests:** {interests_preview}")
                st.markdown("**Focus Areas:**")
                for area in profile['help_areas'][:4]:
                    st.markdown(f"• {area}")
            
            st.markdown("---")
            st.markdown("### 🔒 Privacy")
            st.markdown("⚠️ Data sent to OpenAI")
            st.markdown("✅ Profile stays local")
            st.markdown("✅ You control everything")

if __name__ == "__main__":
    main()