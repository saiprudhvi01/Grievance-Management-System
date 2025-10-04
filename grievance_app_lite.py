"""
Enhanced Grievance System - Lightweight Version
Optimized for compatibility without TensorFlow dependencies
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
from datetime import datetime, timedelta
import json
import logging
from typing import Dict, List, Any, Optional
import uuid
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from database import DatabaseManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LiteGrievanceSystem:
    """
    Lightweight version of the enhanced grievance system
    """
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        
        # Initialize session state
        self._init_session_state()
        
        # Configure page
        st.set_page_config(
            page_title="AI-Powered Grievance System",
            page_icon="🎯",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Apply custom styling
        self._apply_custom_styling()
    
    def _init_session_state(self):
        """Initialize Streamlit session state"""
        if 'user_id' not in st.session_state:
            st.session_state.user_id = None
        if 'username' not in st.session_state:
            st.session_state.username = None
        if 'user_role' not in st.session_state:
            st.session_state.user_role = None
    
    def _apply_custom_styling(self):
        """Apply custom CSS styling"""
        st.markdown("""
        <style>
        .main-header {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .metric-card {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 4px solid #667eea;
        }
        
        .sentiment-positive { color: #28a745; font-weight: bold; }
        .sentiment-negative { color: #dc3545; font-weight: bold; }
        .sentiment-neutral { color: #ffc107; font-weight: bold; }
        </style>
        """, unsafe_allow_html=True)
    
    def analyze_sentiment_lite(self, text: str) -> Dict[str, Any]:
        """Lightweight sentiment analysis using VADER and TextBlob"""
        try:
            # VADER analysis
            vader_scores = self.sentiment_analyzer.polarity_scores(text)
            
            # TextBlob analysis
            blob = TextBlob(text)
            
            # Determine sentiment
            compound_score = vader_scores['compound']
            if compound_score >= 0.05:
                sentiment = 'positive'
                priority = 3
            elif compound_score <= -0.05:
                sentiment = 'negative'
                priority = 1 if compound_score <= -0.5 else 2
            else:
                sentiment = 'neutral'
                priority = 2
            
            # Calculate impact score
            impact_score = min(abs(compound_score) + (len(text.split()) / 100), 1.0)
            
            return {
                'sentiment': sentiment,
                'priority': priority,
                'compound_score': compound_score,
                'impact_score': impact_score,
                'analysis': {
                    'positive': vader_scores['pos'],
                    'negative': vader_scores['neg'],
                    'neutral': vader_scores['neu'],
                    'textblob_polarity': blob.sentiment.polarity
                }
            }
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            return {
                'sentiment': 'neutral',
                'priority': 2,
                'compound_score': 0.0,
                'impact_score': 0.5,
                'analysis': {}
            }
    
    def run(self):
        """Main application runner"""
        # Header
        st.markdown("""
        <div class="main-header">
            <h1>🎯 AI-Powered Grievance System</h1>
            <p>Intelligent complaint resolution with sentiment analysis and smart prioritization</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Check authentication
        if not st.session_state.user_id:
            self._show_login_page()
        else:
            self._show_main_app()
    
    def _show_login_page(self):
        """Show login/registration page"""
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            tab1, tab2 = st.tabs(["Login", "Register"])
            
            with tab1:
                self._show_login_form()
            
            with tab2:
                self._show_registration_form()
    
    def _show_login_form(self):
        """Show login form"""
        st.subheader("Login to Your Account")
        
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            
            if submitted:
                user = self.db_manager.authenticate_user(username, password)
                if user:
                    st.session_state.user_id = user['id']
                    st.session_state.username = user['username']
                    st.session_state.user_role = user['role']
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
    
    def _show_registration_form(self):
        """Show registration form"""
        st.subheader("Create New Account")
        
        with st.form("registration_form"):
            username = st.text_input("Username")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            role = st.selectbox("Role", ["student", "staff", "admin"])
            
            submitted = st.form_submit_button("Register")
            
            if submitted:
                if password != confirm_password:
                    st.error("Passwords do not match")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters")
                elif self.db_manager.create_user(username, email, password, role):
                    st.success("Registration successful! Please login.")
                else:
                    st.error("Username or email already exists")
    
    def _show_main_app(self):
        """Show main application interface"""
        with st.sidebar:
            st.title(f"Welcome, {st.session_state.username}!")
            st.caption(f"Role: {st.session_state.user_role.title()}")
            
            if st.session_state.user_role in ['admin', 'staff']:
                pages = ["Dashboard", "Submit Grievance", "My Grievances", "Admin Panel", "Analytics"]
            else:
                pages = ["Dashboard", "Submit Grievance", "My Grievances"]
            
            selected_page = st.selectbox("Navigate to:", pages)
            
            if st.button("Logout"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
        
        # Show selected page
        if selected_page == "Dashboard":
            self._show_dashboard()
        elif selected_page == "Submit Grievance":
            self._show_submit_grievance()
        elif selected_page == "My Grievances":
            self._show_my_grievances()
        elif selected_page == "Admin Panel":
            self._show_admin_panel()
        elif selected_page == "Analytics":
            self._show_analytics()
    
    def _show_dashboard(self):
        """Show main dashboard"""
        st.header("📊 Dashboard")
        
        analytics = self.db_manager.get_analytics_data()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Grievances", analytics['total_grievances'])
        with col2:
            avg_rating = analytics.get('avg_rating', 0)
            st.metric("Avg Satisfaction", f"{avg_rating:.1f}/5")
        with col3:
            pending_count = analytics['status_counts'].get('Pending', 0)
            st.metric("Pending Cases", pending_count)
        with col4:
            resolved_count = analytics['status_counts'].get('Resolved', 0)
            total = analytics['total_grievances']
            resolution_rate = (resolved_count / total * 100) if total > 0 else 0
            st.metric("Resolution Rate", f"{resolution_rate:.1f}%")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            if analytics['status_counts']:
                fig = px.pie(
                    values=list(analytics['status_counts'].values()),
                    names=list(analytics['status_counts'].keys()),
                    title="Grievance Status Distribution"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if analytics['sentiment_counts']:
                fig = px.bar(
                    x=list(analytics['sentiment_counts'].keys()),
                    y=list(analytics['sentiment_counts'].values()),
                    title="Sentiment Distribution"
                )
                st.plotly_chart(fig, use_container_width=True)
    
    def _show_submit_grievance(self):
        """Show grievance submission form"""
        st.header("📝 Submit New Grievance")
        
        with st.form("grievance_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                title = st.text_input("Title")
                category = st.selectbox("Category", ["Academic", "Hostel", "Infrastructure", "Administration", "Other"])
            
            with col2:
                anonymous = st.checkbox("Submit anonymously")
            
            description = st.text_area("Detailed Description", height=150)
            
            submitted = st.form_submit_button("Submit Grievance", type="primary")
            
            if submitted and title and description:
                try:
                    with st.spinner("Analyzing grievance..."):
                        analysis = self.analyze_sentiment_lite(description)
                    
                    user_id = None if anonymous else st.session_state.user_id
                    grievance_id = self.db_manager.submit_grievance(
                        user_id or 0,
                        title,
                        category,
                        description,
                        analysis['sentiment'],
                        analysis['priority']
                    )
                    
                    st.success("✅ Grievance submitted successfully!")
                    
                    with st.expander("📊 AI Analysis Results", expanded=True):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            sentiment = analysis['sentiment']
                            st.markdown(f'**Sentiment:** <span class="sentiment-{sentiment}">{sentiment.title()}</span>', 
                                      unsafe_allow_html=True)
                        
                        with col2:
                            priority_labels = {1: "High", 2: "Medium", 3: "Low"}
                            st.write(f"**Priority:** {priority_labels[analysis['priority']]}")
                        
                        with col3:
                            st.metric("Impact Score", f"{analysis['impact_score']:.3f}")
                
                except Exception as e:
                    st.error(f"Error submitting grievance: {e}")
            
            elif submitted:
                st.error("Please fill in all required fields.")
    
    def _show_my_grievances(self):
        """Show user's grievances"""
        st.header("📋 My Grievances")
        
        grievances = self.db_manager.get_grievances(
            user_id=st.session_state.user_id if st.session_state.user_role != 'admin' else None
        )
        
        if not grievances:
            st.info("You haven't submitted any grievances yet.")
            return
        
        for grievance in grievances:
            with st.expander(f"#{grievance['id']} - {grievance['title']}", expanded=False):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write("**Description:**")
                    st.write(grievance['description'])
                    
                    if grievance['response']:
                        st.write("**Response:**")
                        st.info(grievance['response'])
                
                with col2:
                    st.write(f"**Status:** {grievance['status']}")
                    st.write(f"**Category:** {grievance['category']}")
                    st.write(f"**Priority:** {grievance['priority']}")
                    st.write(f"**Sentiment:** {grievance['sentiment']}")
                    st.write(f"**Submitted:** {grievance['created_at']}")
    
    def _show_admin_panel(self):
        """Show admin panel"""
        if st.session_state.user_role not in ['admin', 'staff']:
            st.error("Access denied. Admin privileges required.")
            return
        
        st.header("🔧 Admin Panel")
        
        grievances = self.db_manager.get_grievances()
        
        if not grievances:
            st.info("No grievances to manage.")
            return
        
        for grievance in grievances[:10]:  # Show latest 10
            with st.expander(f"#{grievance['id']} - {grievance['title']} [{grievance['status']}]"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write("**Description:**")
                    st.write(grievance['description'])
                    
                    response = st.text_area(
                        "Response",
                        value=grievance['response'] or "",
                        key=f"response_{grievance['id']}"
                    )
                
                with col2:
                    st.write(f"**User:** {grievance['username']}")
                    st.write(f"**Category:** {grievance['category']}")
                    st.write(f"**Priority:** {grievance['priority']}")
                    st.write(f"**Sentiment:** {grievance['sentiment']}")
                    
                    new_status = st.selectbox(
                        "Status",
                        ["Pending", "In Progress", "Resolved"],
                        index=["Pending", "In Progress", "Resolved"].index(grievance['status']),
                        key=f"status_{grievance['id']}"
                    )
                    
                    if st.button("Update", key=f"update_{grievance['id']}"):
                        self.db_manager.update_grievance_status(
                            grievance['id'], new_status, response
                        )
                        st.success("Grievance updated!")
                        st.rerun()
    
    def _show_analytics(self):
        """Show analytics dashboard"""
        st.header("📊 Analytics Dashboard")
        
        grievances = self.db_manager.get_grievances()
        
        if not grievances:
            st.warning("No data available for analysis.")
            return
        
        df = pd.DataFrame(grievances)
        df['created_at'] = pd.to_datetime(df['created_at'])
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Grievances", len(df))
        with col2:
            resolution_rate = len(df[df['status'] == 'Resolved']) / len(df) * 100
            st.metric("Resolution Rate", f"{resolution_rate:.1f}%")
        with col3:
            avg_rating = df['rating'].mean() if 'rating' in df and df['rating'].notna().any() else 0
            st.metric("Avg Rating", f"{avg_rating:.1f}/5")
        
        # Sentiment over time
        sentiment_by_date = df.groupby([df['created_at'].dt.date, 'sentiment']).size().unstack(fill_value=0)
        if not sentiment_by_date.empty:
            fig = px.line(sentiment_by_date, title="Sentiment Trends Over Time")
            st.plotly_chart(fig, use_container_width=True)
        
        # Category analysis
        col1, col2 = st.columns(2)
        
        with col1:
            category_counts = df['category'].value_counts()
            fig = px.bar(x=category_counts.index, y=category_counts.values, title="Grievances by Category")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            priority_counts = df['priority'].value_counts().sort_index()
            fig = px.pie(values=priority_counts.values, names=[f"Priority {p}" for p in priority_counts.index], 
                        title="Priority Distribution")
            st.plotly_chart(fig, use_container_width=True)

# Main application entry point
if __name__ == "__main__":
    app = LiteGrievanceSystem()
    app.run()
