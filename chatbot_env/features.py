import streamlit as st
import json
import pandas as pd
from datetime import datetime, timedelta
import os
from memory import load_conversation_history

def show_chat_statistics():
    """Show statistics about chat usage"""
    st.header("📊 Your Chat Statistics")
    
    try:
        history = load_conversation_history()
        
        if not history:
            st.info("💡 No conversations yet! Start chatting to see your statistics.")
            return
        
        # Basic stats in columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Conversations", len(history))
        
        with col2:
            try:
                latest_date = history[-1].get('timestamp', '').split('T')[0] if history else 'N/A'
                if latest_date == 'N/A':
                    latest_date = history[-1].get('date', 'Unknown')
                st.metric("Last Chat", latest_date)
            except Exception:
                st.metric("Last Chat", "Unknown")
        
        with col3:
            try:
                total_words = 0
                for conv in history:
                    # Use stored word counts if available, otherwise calculate
                    user_words = conv.get('user_word_count', len(conv.get('user', '').split()))
                    assistant_words = conv.get('assistant_word_count', len(conv.get('assistant', '').split()))
                    total_words += user_words + assistant_words
                st.metric("Total Words", f"{total_words:,}")
            except Exception:
                st.metric("Total Words", "Error")
        
        with col4:
            try:
                unique_dates = set(conv.get('date', datetime.now().strftime("%Y-%m-%d")) for conv in history)
                avg_per_day = len(history) / max(1, len(unique_dates))
                st.metric("Avg per Day", f"{avg_per_day:.1f}")
            except Exception:
                st.metric("Avg per Day", "Error")
        
        # Domain breakdown
        st.subheader("📈 Topics You Discuss Most")
        
        try:
            domains = {}
            for conv in history:
                domain = conv.get('domain', 'general')
                domains[domain] = domains.get(domain, 0) + 1
            
            if domains:
                # Create DataFrame safely
                domain_items = list(domains.items())
                if domain_items:
                    domain_df = pd.DataFrame(domain_items, columns=['Topic', 'Count'])
                    domain_df = domain_df.sort_values('Count', ascending=True)
                    
                    # Display chart
                    try:
                        st.bar_chart(domain_df.set_index('Topic'))
                    except Exception as e:
                        st.error(f"Error creating chart: {e}")
                        # Fallback display
                        for topic, count in sorted(domains.items(), key=lambda x: x[1], reverse=True):
                            st.write(f"**{topic.title()}**: {count} conversations")
                    
                    # Show percentages
                    total = sum(domains.values())
                    st.write("**Breakdown:**")
                    for domain, count in sorted(domains.items(), key=lambda x: x[1], reverse=True):
                        percentage = (count / total) * 100 if total > 0 else 0
                        st.write(f"• **{domain.title()}**: {count} conversations ({percentage:.1f}%)")
            else:
                st.info("No domain data available yet")
        except Exception as e:
            st.error(f"Error processing domain statistics: {e}")
        
        # Recent activity
        st.subheader("📅 Daily Activity (Last 7 Days)")
        
        try:
            dates = {}
            for conv in history:
                date = conv.get('date', conv.get('timestamp', '').split('T')[0] if conv.get('timestamp') else 'unknown')
                if date != 'unknown':
                    dates[date] = dates.get(date, 0) + 1
            
            if dates:
                # Get last 7 days of data
                recent_dates = sorted(dates.items())[-7:]
                if recent_dates:
                    try:
                        dates_df = pd.DataFrame(recent_dates, columns=['Date', 'Conversations'])
                        st.line_chart(dates_df.set_index('Date'))
                    except Exception as e:
                        st.error(f"Error creating activity chart: {e}")
                        # Fallback display
                        st.write("Recent activity:")
                        for date, count in recent_dates:
                            st.write(f"- {date}: {count} conversations")
            else:
                st.info("No recent activity data available")
        except Exception as e:
            st.error(f"Error processing activity data: {e}")
        
    except Exception as e:
        st.error(f"Error loading chat statistics: {e}")
        st.info("Please check if your conversation history file is accessible.")

def export_data():
    """Export user data"""
    st.header("📥 Export Your Data")
    st.write("Download all your data including conversations and profile.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💬 Conversation History")
        
        try:
            history = load_conversation_history()
            
            if history:
                # Create detailed export data
                export_data = []
                for i, conv in enumerate(history):
                    try:
                        # Extract date and time safely
                        timestamp = conv.get('timestamp', '')
                        if timestamp:
                            if 'T' in timestamp:
                                date_part = timestamp.split('T')[0]
                                time_part = timestamp.split('T')[1][:8] if len(timestamp.split('T')) > 1 else ''
                            else:
                                date_part = conv.get('date', 'Unknown')
                                time_part = ''
                        else:
                            date_part = conv.get('date', 'Unknown')
                            time_part = ''
                        
                        export_data.append({
                            'Conversation_ID': i + 1,
                            'Date': date_part,
                            'Time': time_part,
                            'Your_Message': conv.get('user', ''),
                            'Assistant_Response': conv.get('assistant', ''),
                            'Domain': conv.get('domain', 'general'),
                            'Your_Word_Count': conv.get('user_word_count', len(conv.get('user', '').split())),
                            'Response_Word_Count': conv.get('assistant_word_count', len(conv.get('assistant', '').split())),
                            'Timestamp_Full': timestamp
                        })
                    except Exception as e:
                        st.warning(f"Error processing conversation {i+1}: {e}")
                        continue
                
                if export_data:
                    try:
                        df = pd.DataFrame(export_data)
                        csv = df.to_csv(index=False)
                        
                        st.download_button(
                            label="📊 Download Chat History (CSV)",
                            data=csv,
                            file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                            mime='text/csv',
                            help="Download all your conversations in CSV format"
                        )
                        
                        st.write(f"**{len(export_data)} conversations** ready for download")
                        
                        # Show preview
                        with st.expander("📋 Preview Export Data"):
                            st.dataframe(df.head(), use_container_width=True)
                            
                    except Exception as e:
                        st.error(f"Error creating export file: {e}")
                else:
                    st.warning("No valid conversation data found to export")
            else:
                st.info("No conversations to export yet.")
        except Exception as e:
            st.error(f"Error accessing conversation history: {e}")
    
    with col2:
        st.subheader("👤 Profile Data")
        
        try:
            if os.path.exists('user_profile.json'):
                with open('user_profile.json', 'r', encoding='utf-8') as f:
                    profile = json.load(f)
                
                if profile:
                    profile_json = json.dumps(profile, indent=2, ensure_ascii=False)
                    
                    st.download_button(
                        label="👤 Download Profile (JSON)",
                        data=profile_json,
                        file_name=f"my_profile_{datetime.now().strftime('%Y%m%d')}.json",
                        mime='application/json',
                        help="Download your profile information"
                    )
                    
                    # Show profile preview
                    st.write("**Profile Preview:**")
                    st.write(f"• **Name**: {profile.get('name', 'Not set')}")
                    st.write(f"• **Role**: {profile.get('role', 'Not set')}")
                    st.write(f"• **Communication Style**: {profile.get('communication_style', 'Not set')}")
                    st.write(f"• **Help Areas**: {len(profile.get('help_areas', []))} selected")
                    
                    # Profile size info
                    st.info(f"Profile size: {len(profile_json)} characters")
                else:
                    st.warning("Profile file exists but appears to be empty")
            else:
                st.info("No profile to export. Create one first!")
        except json.JSONDecodeError:
            st.error("Profile file is corrupted and cannot be exported")
        except Exception as e:
            st.error(f"Error accessing profile data: {e}")
        
        # Export statistics
        st.subheader("📈 Usage Statistics")
        
        try:
            history = load_conversation_history()
            if history:
                stats = {
                    "export_date": datetime.now().isoformat(),
                    "total_conversations": len(history),
                    "date_range": {
                        "first_conversation": min(conv.get('timestamp', '') for conv in history if conv.get('timestamp')),
                        "last_conversation": max(conv.get('timestamp', '') for conv in history if conv.get('timestamp'))
                    },
                    "domains": {},
                    "daily_usage": {}
                }
                
                # Calculate domain and daily stats
                for conv in history:
                    domain = conv.get('domain', 'general')
                    stats["domains"][domain] = stats["domains"].get(domain, 0) + 1
                    
                    date = conv.get('date', 'unknown')
                    stats["daily_usage"][date] = stats["daily_usage"].get(date, 0) + 1
                
                stats_json = json.dumps(stats, indent=2, ensure_ascii=False)
                
                st.download_button(
                    label="📈 Download Statistics (JSON)",
                    data=stats_json,
                    file_name=f"usage_stats_{datetime.now().strftime('%Y%m%d')}.json",
                    mime='application/json',
                    help="Download your usage statistics"
                )
            else:
                st.info("No statistics to export yet")
        except Exception as e:
            st.error(f"Error generating statistics: {e}")

def show_conversation_insights():
    """Show insights about conversations"""
    st.header("🔍 Conversation Insights")
    
    try:
        history = load_conversation_history()
        
        if not history:
            st.info("Start chatting to see insights!")
            return
        
        # Most common topics
        st.subheader("💬 What You Talk About Most")
        
        try:
            all_text = ' '.join([conv.get('user', '') for conv in history])
            words = all_text.lower().split()
            
            # Filter out common words
            stop_words = {
                'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 
                'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 
                'will', 'would', 'could', 'should', 'may', 'might', 'can', 'i', 'you', 'he', 'she', 
                'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'hers', 
                'its', 'our', 'their', 'this', 'that', 'these', 'those'
            }
            
            word_counts = {}
            for word in words:
                # Clean word and check criteria
                clean_word = ''.join(c for c in word if c.isalpha()).lower()
                if len(clean_word) > 3 and clean_word not in stop_words:
                    word_counts[clean_word] = word_counts.get(clean_word, 0) + 1
            
            if word_counts:
                top_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:15]
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    try:
                        words_df = pd.DataFrame(top_words, columns=['Word', 'Frequency'])
                        st.bar_chart(words_df.set_index('Word'))
                    except Exception as e:
                        st.error(f"Error creating word chart: {e}")
                        # Fallback display
                        st.write("**Top words you use:**")
                        for word, count in top_words[:10]:
                            st.write(f"• **{word}**: {count} times")
                
                with col2:
                    st.write("**Top words you use:**")
                    for word, count in top_words[:8]:
                        st.write(f"• **{word}**: {count} times")
        except Exception as e:
            st.error(f"Error analyzing word usage: {e}")
        
        # Question patterns
        st.subheader("❓ Your Question Patterns")
        
        try:
            questions = [conv.get('user', '') for conv in history if '?' in conv.get('user', '')]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Questions Asked", len(questions))
                if len(history) > 0:
                    question_percentage = (len(questions) / len(history)) * 100
                    st.metric("Questions vs Statements", f"{question_percentage:.1f}%")
            
            with col2:
                # Common question starters
                question_starters = {}
                for q in questions:
                    words = q.strip().split()
                    if words:
                        first_word = words[0].lower().rstrip('?,!.')
                        if first_word in ['what', 'how', 'why', 'when', 'where', 'who', 'can', 'could', 'should', 'would', 'is', 'are', 'do', 'does']:
                            question_starters[first_word] = question_starters.get(first_word, 0) + 1
                
                if question_starters:
                    st.write("**How you start questions:**")
                    for starter, count in sorted(question_starters.items(), key=lambda x: x[1], reverse=True)[:5]:
                        st.write(f"• **{starter.title()}**: {count} times")
        except Exception as e:
            st.error(f"Error analyzing question patterns: {e}")
        
        # Conversation evolution
        st.subheader("📈 How Your Conversations Have Evolved")
        
        try:
            if len(history) >= 10:
                # Compare first 5 vs last 5 conversations
                first_five = history[:5]
                last_five = history[-5:]
                
                first_avg_length = sum(len(conv.get('user', '').split()) for conv in first_five) / 5
                last_avg_length = sum(len(conv.get('user', '').split()) for conv in last_five) / 5
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("First 5 conversations", f"{first_avg_length:.1f} words avg")
                
                with col2:
                    st.metric("Recent 5 conversations", f"{last_avg_length:.1f} words avg")
                
                change = last_avg_length - first_avg_length
                if change > 0:
                    st.write(f"📈 You're writing {change:.1f} more words on average")
                elif change < 0:
                    st.write(f"📉 You're writing {abs(change):.1f} fewer words on average")
                else:
                    st.write("📊 Your message length is consistent")
            else:
                st.info("Need at least 10 conversations to show evolution trends")
        except Exception as e:
            st.error(f"Error analyzing conversation evolution: {e}")
            
    except Exception as e:
        st.error(f"Error loading conversation insights: {e}")