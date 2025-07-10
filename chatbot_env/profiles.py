import streamlit as st
import json
import os
from datetime import datetime

def save_user_profile(profile_data):
    """Save user profile to a file"""
    if not profile_data:
        st.error("No profile data to save")
        return False
    
    try:
        # Ensure the profile data is valid
        required_fields = ['name', 'role', 'communication_style']
        for field in required_fields:
            if not profile_data.get(field):
                st.error(f"Missing required field: {field}")
                return False
        
        # Save to file
        with open('user_profile.json', 'w', encoding='utf-8') as f:
            json.dump(profile_data, f, indent=2, ensure_ascii=False)
        return True
    except PermissionError:
        st.error("Permission denied: Cannot write to user_profile.json")
        return False
    except json.JSONEncodeError as e:
        st.error(f"Error encoding profile data: {e}")
        return False
    except Exception as e:
        st.error(f"Error saving profile: {e}")
        return False

def load_user_profile():
    """Load user profile from file"""
    try:
        if os.path.exists('user_profile.json'):
            with open('user_profile.json', 'r', encoding='utf-8') as f:
                profile = json.load(f)
                
                # Validate loaded profile
                if not isinstance(profile, dict):
                    st.warning("Invalid profile format detected. Please recreate your profile.")
                    return None
                
                return profile
        return None
    except json.JSONDecodeError:
        st.error("Profile file is corrupted. Please recreate your profile.")
        return None
    except PermissionError:
        st.error("Permission denied: Cannot read user_profile.json")
        return None
    except Exception as e:
        st.error(f"Error loading profile: {e}")
        return None

def show_profile_setup():
    """Show the profile setup page"""
    st.title("👤 Set Up Your Personal Profile")
    st.write("Let's personalize your assistant! This information stays on your computer.")
    
    # Load existing profile if it exists
    existing_profile = load_user_profile()
    
    with st.form("profile_form"):
        st.markdown("### Basic Information")
        
        name = st.text_input(
            "What's your name? *", 
            value=existing_profile.get('name', '') if existing_profile else '',
            max_chars=50,
            help="This will be used to personalize responses"
        )
        
        role = st.selectbox(
            "What's your main role? *", 
            ["Student", "Working Professional", "Parent", "Freelancer", "Retired", "Other"],
            index=0 if not existing_profile else (
                ["Student", "Working Professional", "Parent", "Freelancer", "Retired", "Other"].index(
                    existing_profile.get('role', 'Student')
                ) if existing_profile.get('role') in ["Student", "Working Professional", "Parent", "Freelancer", "Retired", "Other"] else 0
            )
        )
        
        work_area = st.text_input(
            "What do you do for work/study?",
            value=existing_profile.get('work_area', '') if existing_profile else '',
            max_chars=100,
            placeholder="e.g., 'Software Engineering', 'Marketing', 'High School'"
        )
        
        st.markdown("### Personal Details")
        
        family_info = st.text_area(
            "Tell me about your family (optional)",
            value=existing_profile.get('family_info', '') if existing_profile else '',
            max_chars=200,
            placeholder="e.g., 'Married with 2 kids' or 'Single, live with parents'"
        )
        
        interests = st.text_area(
            "What are your hobbies and interests?",
            value=existing_profile.get('interests', '') if existing_profile else '',
            max_chars=300,
            placeholder="e.g., 'Reading, cooking, soccer, video games, travel'"
        )
        
        st.markdown("### Communication Preferences")
        
        communication_styles = ["Casual and friendly", "Professional", "Direct and brief", "Detailed explanations"]
        communication_style = st.selectbox(
            "How do you prefer to communicate? *",
            communication_styles,
            index=0 if not existing_profile else (
                communication_styles.index(existing_profile.get('communication_style', 'Casual and friendly'))
                if existing_profile.get('communication_style') in communication_styles else 0
            )
        )
        
        help_areas_options = [
            "Work tasks", "Family planning", "Entertainment suggestions", 
            "Learning new things", "Health and fitness", "Financial planning"
        ]
        help_areas = st.multiselect(
            "What would you like help with?",
            help_areas_options,
            default=existing_profile.get('help_areas', []) if existing_profile else []
        )
        
        work_hours_options = ["Morning person", "Night owl", "Standard 9-5", "Flexible schedule"]
        work_hours = st.selectbox(
            "When are you most active?",
            work_hours_options,
            index=0 if not existing_profile else (
                work_hours_options.index(existing_profile.get('work_hours', 'Flexible schedule'))
                if existing_profile.get('work_hours') in work_hours_options else 0
            )
        )
        
        st.markdown("---")
        st.markdown("*Required fields")
        
        submit = st.form_submit_button("💾 Save My Profile", type="primary")
        
        if submit:
            # Validate required fields
            if not name.strip():
                st.error("Please enter your name")
                return None
            
            if not role:
                st.error("Please select your role")
                return None
            
            if not communication_style:
                st.error("Please select your communication style")
                return None
            
            # Create profile object
            profile = {
                "name": name.strip(),
                "role": role,
                "work_area": work_area.strip(),
                "family_info": family_info.strip(),
                "interests": interests.strip(),
                "communication_style": communication_style,
                "help_areas": help_areas,
                "work_hours": work_hours,
                "created_date": existing_profile.get('created_date', datetime.now().isoformat()) if existing_profile else datetime.now().isoformat(),
                "updated_date": datetime.now().isoformat()
            }
            
            # Save profile
            if save_user_profile(profile):
                st.success("✅ Profile saved successfully!")
                st.balloons()
                st.info("🚀 Now go to the Chat page to see personalized responses!")
                
                # Show success metrics
                st.markdown("### 📊 Profile Summary")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Profile Completeness", f"{len([v for v in profile.values() if v])}/{len(profile)}")
                with col2:
                    st.metric("Help Areas Selected", len(help_areas))
                
                return profile
            else:
                st.error("Failed to save profile. Please try again.")
    
    # Show current profile if exists
    if existing_profile:
        st.markdown("---")
        st.subheader("📄 Your Current Profile")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**👤 Name:** {existing_profile.get('name', 'Not set')}")
            st.write(f"**💼 Role:** {existing_profile.get('role', 'Not set')}")
            st.write(f"**🏢 Work/Study:** {existing_profile.get('work_area', 'Not specified')}")
            st.write(f"**🏠 Family:** {existing_profile.get('family_info', 'Not specified')}")
        
        with col2:
            st.write(f"**💬 Communication Style:** {existing_profile.get('communication_style', 'Not set')}")
            st.write(f"**🕐 Work Hours:** {existing_profile.get('work_hours', 'Not set')}")
            st.write(f"**🎯 Help Areas:** {', '.join(existing_profile.get('help_areas', [])) or 'None selected'}")
            st.write(f"**🎨 Interests:** {existing_profile.get('interests', 'Not specified')}")
        
        # Profile actions
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Delete Profile", type="secondary"):
                if st.button("⚠️ Confirm Delete", type="secondary"):
                    try:
                        if os.path.exists('user_profile.json'):
                            os.remove('user_profile.json')
                            st.success("Profile deleted successfully!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error deleting profile: {e}")
        
        with col2:
            # Export profile button
            profile_json = json.dumps(existing_profile, indent=2)
            st.download_button(
                label="📥 Export Profile",
                data=profile_json,
                file_name=f"profile_backup_{datetime.now().strftime('%Y%m%d')}.json",
                mime='application/json'
            )
    
    return None