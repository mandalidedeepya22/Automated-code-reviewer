"""
Main Streamlit application for AI-Powered Automated Code Reviewer.
Frontend UI for code review functionality with authentication.
"""

import streamlit as st
import os
import json
import time
from pathlib import Path
from datetime import datetime
import base64

# Import custom modules
from database.db import get_db
from utils.code_parser import CodeParser
from utils.static_analyzer import StaticAnalyzer
from utils.security_checker import SecurityChecker
from models.ai_reviewer import AIReviewer
from utils.report_generator import ReportGenerator
from utils.github_fetcher import GitHubFetcher

# Configure Streamlit
st.set_page_config(
    page_title="AI Code Reviewer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
def load_custom_css():
    st.markdown("""
    <style>
        .main {
            padding: 0;
        }
        
        .stTabs [data-baseweb="tab-list"] button {
            font-size: 16px;
            padding: 10px 20px;
        }
        
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        
        .issue-critical { border-left: 4px solid #d32f2f; }
        .issue-high { border-left: 4px solid #f57c00; }
        .issue-medium { border-left: 4px solid #fbc02d; }
        .issue-low { border-left: 4px solid #388e3c; }
        
        .success-message {
            background-color: #f1f8e9;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #388e3c;
        }
        
        .error-message {
            background-color: #ffebee;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #d32f2f;
        }
    </style>
    """, unsafe_allow_html=True)

load_custom_css()

# Initialize session state
if 'user' not in st.session_state:
    st.session_state.user = None
if 'review_data' not in st.session_state:
    st.session_state.review_data = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'

# Initialize database
db = get_db()

# Initialize analysis modules
code_parser = CodeParser()
static_analyzer = StaticAnalyzer()
security_checker = SecurityChecker()
ai_reviewer = AIReviewer()
report_generator = ReportGenerator()


def show_login_page():
    """Display login/register page."""
    st.title("🔐 AI Code Reviewer")
    
    tab1, tab2 = st.tabs(["Sign In", "Create Account"])
    
    with tab1:
        st.subheader("Sign In")
        
        login_username = st.text_input("Username", key="login_username")
        login_password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Sign In", key="login_btn", use_container_width=True):
            if not login_username:
                st.error("Please enter a username")
            elif not login_password:
                st.error("Please enter a password")
            else:
                # Debug: Show what we're trying to authenticate
                st.write(f"Attempting to login as: {login_username}")
                
                user = db.authenticate_user(login_username, login_password)
                
                if user:
                    st.session_state.user = user
                    st.success(f"Welcome back, {user['username']}!")
                    st.rerun()
                else:
                    # Debug: Show more specific error
                    existing_user = db.get_user_by_username(login_username)
                    if existing_user is None:
                        st.error(f"User '{login_username}' not found. Please register first.")
                    else:
                        st.error("Incorrect password. Please try again.")
    
    with tab2:
        st.subheader("Create Account")
        
        new_username = st.text_input("Username", key="register_username")
        new_email = st.text_input("Email", key="register_email")
        new_password = st.text_input("Password", type="password", key="register_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="register_confirm")
        
        if st.button("Sign Up", key="register_btn", use_container_width=True):
            # Validation
            if not new_username:
                st.error("Username is required")
            elif not new_email:
                st.error("Email is required")
            elif '@' not in new_email:
                st.error("Please enter a valid email address")
            elif new_password != confirm_password:
                st.error("Passwords do not match")
            elif len(new_password) < 6:
                st.error("Password must be at least 6 characters")
            else:
                # Attempt registration
                st.write(f"Attempting to register: {new_username}, {new_email}")
                
                if db.register_user(new_username, new_email, new_password):
                    st.success("Account created successfully! Please sign in.")
                else:
                    # Check what went wrong
                    existing = db.get_user_by_username(new_username)
                    if existing:
                        st.error("Username already exists. Please choose another.")
                    else:
                        st.error("Registration failed. Please try again.")


def show_sidebar():
    """Display sidebar navigation."""
    with st.sidebar:
        st.title("🔍 Code Reviewer")
        
        if st.session_state.user:
            st.write(f"👤 {st.session_state.user['username']}")
            
            st.divider()
            
            # Navigation
            st.subheader("Navigation")
            if st.button("🏠 Home", use_container_width=True):
                st.session_state.current_page = 'home'
                st.rerun()
            
            if st.button("📝 Review Code", use_container_width=True):
                st.session_state.current_page = 'review'
                st.rerun()
            
            if st.button("📚 Review History", use_container_width=True):
                st.session_state.current_page = 'history'
                st.rerun()
            
            if st.button("⚙️ Settings", use_container_width=True):
                st.session_state.current_page = 'settings'
                st.rerun()
            
            st.divider()
            
            # Logout
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.user = None
                st.session_state.current_page = 'home'
                st.rerun()
        else:
            st.info("Please sign in to access all features")


def show_home_page():
    """Display home page."""
    st.title("🔍 AI-Powered Code Reviewer")
    
    st.markdown("""
    Welcome to the AI-Powered Automated Code Reviewer! This tool helps you identify:
    
    - 🐛 **Bugs & Logic Errors** - Potential runtime issues
    - 🔒 **Security Vulnerabilities** - SQL injection, XSS, credential exposure
    - ⚡ **Performance Issues** - Inefficient algorithms and bad practices
    - 📊 **Code Quality Issues** - Complexity, duplication, naming conventions
    - 📝 **Missing Documentation** - Undocumented functions and modules
    - 🎯 **Best Practice Violations** - SOLID principles, design patterns
    """)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>8</h3>
            <p>Languages Supported</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>12+</h3>
            <p>Issue Types</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>3</h3>
            <p>Input Methods</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>4</h3>
            <p>Report Formats</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.subheader("📋 Supported Languages")
    
    languages = ["Python", "JavaScript/TypeScript", "Java", "C/C++", "SQL", "HTML/CSS", "Go", "Rust"]
    
    cols = st.columns(4)
    for i, lang in enumerate(languages):
        with cols[i % 4]:
            st.write(f"✓ {lang}")
    
    st.markdown("---")
    
    st.subheader("🚀 Quick Start")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("""
        **Option 1: Paste Code**
        1. Go to Review Code tab
        2. Select "Paste Code"
        3. Paste your code
        4. Click "Review Code"
        """)
    
    with col2:
        st.write("""
        **Option 2: Upload File**
        1. Go to Review Code tab
        2. Select "Upload File"
        3. Choose your file
        4. Review results
        """)


def show_review_page():
    """Display code review page."""
    st.title("📝 Code Review")
    
    # Input method selection
    input_method = st.radio("Select Input Method", 
                           ["Paste Code", "Upload File", "Upload ZIP", "GitHub Repo"],
                           horizontal=True)
    
    st.divider()
    
    code = ""
    language = ""
    filename = "code"
    
    if input_method == "Paste Code":
        language = st.selectbox("Programming Language", 
                               ["Python", "JavaScript", "Java", "C++", "SQL", "HTML", "CSS", "Go", "Auto-detect"])
        
        code = st.text_area("Paste your code here:", height=400, key="code_paste")
        
        if code:
            if language == "Auto-detect":
                language = code_parser.detect_language("code", code)
            
            filename = f"code.{language.lower()}"
    
    elif input_method == "Upload File":
        uploaded_file = st.file_uploader("Choose a code file", 
                                        type=['py', 'js', 'ts', 'java', 'cpp', 'c', 'sql', 'html', 'css', 'go'])
        
        if uploaded_file:
            filename = uploaded_file.name
            code = uploaded_file.read().decode('utf-8')
            language = code_parser.detect_language(filename)
    
    elif input_method == "Upload ZIP":
        uploaded_zip = st.file_uploader("Choose a ZIP file", type=['zip'])
        
        if uploaded_zip:
            # Save temp ZIP
            zip_path = f"temp_{uploaded_zip.name}"
            with open(zip_path, 'wb') as f:
                f.write(uploaded_zip.getvalue())
            
            files = code_parser.extract_from_zip(zip_path)
            
            if files:
                st.success(f"Extracted {len(files)} code files")
                
                selected_file = st.selectbox("Select file to review", list(files.keys()))
                if selected_file:
                    code = files[selected_file]
                    filename = selected_file
                    language = code_parser.detect_language(filename)
                    st.write(f"Selected: {filename} ({language})")
            
            # Clean up
            if os.path.exists(zip_path):
                os.remove(zip_path)
    
    elif input_method == "GitHub Repo":
        st.info("GitHub integration requires a personal access token in settings")
        
        saved_token = db.get_github_token(st.session_state.user['id']) if st.session_state.user else None
        github_token = st.text_input("GitHub Token", value=st.session_state.get('github_token', saved_token or ''), type="password")
        repo_url = st.text_input("Repository URL", placeholder="https://github.com/owner/repo")
        
        if st.button("Fetch Repository"):
            token = github_token or saved_token
            if not token:
                st.error("Please provide a GitHub token.")
            else:
                st.session_state.github_token = token
                github = GitHubFetcher(token)
                is_valid, msg = github.validate_connection()
                
                if is_valid:
                    st.success(msg)
                    repo_info = github.fetch_repository(repo_url)
                    if repo_info:
                        st.session_state.github_repo_info = repo_info
                        parsed = github._parse_repo_url(repo_url)
                        if parsed:
                            owner, repo = parsed
                            st.session_state.github_owner_repo = (owner, repo)
                            files = github.get_repository_files(owner, repo)
                            supported_files = [
                                f for f in files
                                if any(f.get('name', '').lower().endswith(ext) for ext in [
                                    '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.c',
                                    '.cpp', '.h', '.hpp', '.sql', '.html', '.css', '.go', '.rs'
                                ])
                            ]
                            st.session_state.github_repo_files = supported_files
                        else:
                            st.error("Unable to parse repository owner and name from the URL.")
                    else:
                        st.error("Unable to fetch repository details. Check the URL and token.")
                else:
                    st.error(msg)

        # Show repository results
        if st.session_state.get('github_repo_info'):
            info = st.session_state.github_repo_info
            st.write(f"**{info.get('name')}** - {info.get('description', 'No description')}  ")
            st.write(f"Language: {info.get('language', 'Unknown')} | Stars: {info.get('stars', 0)} | Forks: {info.get('forks', 0)}")

        if st.session_state.get('github_repo_files'):
            file_options = [f.get('path') for f in st.session_state.github_repo_files]
            selected_file = st.selectbox("Select a file to review", file_options, key="github_file_select")
            if selected_file:
                owner, repo = st.session_state.get('github_owner_repo', (None, None))
                if owner and repo:
                    github = GitHubFetcher(st.session_state.github_token)
                    file_content = github.get_file_content(owner, repo, selected_file)
                    if file_content:
                        code = file_content
                        filename = selected_file
                        language = code_parser.detect_language(filename)
                        st.write(f"Loaded **{filename}** from GitHub repository.")
                    else:
                        st.error("Unable to load selected file content.")
                else:
                    st.error("Repository owner and name could not be resolved.")
    
    # Review button
    if code:
        is_valid, validation_msg = code_parser.validate_code(code, language.lower() if language != "Auto-detect" else "unknown")
        
        if not is_valid:
            st.error(f"❌ {validation_msg}")
        else:
            if st.button("🔍 Review Code", use_container_width=True, key="review_btn"):
                with st.spinner("Analyzing code..."):
                    try:
                        start_time = time.time()
                        
                        # Parse code
                        code_clean = code_parser.clean_code(code)
                        metrics = code_parser.get_code_metrics(code_clean)
                        
                        # Static analysis
                        analysis_results = {}
                        if language.lower() == 'python':
                            analysis_results = static_analyzer.analyze_python(code_clean)
                        elif language.lower() in ['javascript', 'typescript']:
                            analysis_results = static_analyzer.analyze_javascript(code_clean)
                        elif language.lower() == 'java':
                            analysis_results = static_analyzer.analyze_java(code_clean)
                        elif language.lower() == 'sql':
                            analysis_results = static_analyzer.analyze_sql(code_clean)
                        
                        # AI Review
                        review = ai_reviewer.review_code(code_clean, language.lower(), analysis_results)
                        review['code_metrics'] = metrics
                        
                        # Security Check
                        security = security_checker.check_security(code_clean, language.lower())
                        review['security_details'] = security
                        
                        # Calculate final scores
                        if security['security_score'] < review['security_score']:
                            review['security_score'] = security['security_score']
                        
                        review['analysis_time'] = time.time() - start_time
                        review['filename'] = filename
                        
                        st.session_state.review_data = review
                        
                        # Save to database
                        if st.session_state.user:
                            try:
                                review_id = db.save_review(
                                    user_id=st.session_state.user['id'],
                                    filename=filename,
                                    language=language.lower(),
                                    file_size=len(code),
                                    code_content=code_clean[:5000],
                                    review_result=json.dumps(review),
                                    quality_score=review['quality_score'],
                                    security_score=review['security_score'],
                                    issues_count=len(review['issues']),
                                    analysis_time=review['analysis_time']
                                )
                                
                                db.save_review_issues(review_id, review['issues'])
                            except Exception as e:
                                st.warning(f"Could not save review: {e}")
                        
                        st.success(f"✅ Review completed in {review['analysis_time']:.2f}s")
                        
                    except Exception as e:
                        st.error(f"❌ Error during review: {str(e)}")
    
    # Display results
    if st.session_state.review_data:
        st.divider()
        show_review_results(st.session_state.review_data)


def show_review_results(review_data):
    """Display review results."""
    st.subheader("📊 Review Results")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Quality Score", f"{review_data['quality_score']:.0f}/100")
    
    with col2:
        st.metric("Security Score", f"{review_data['security_score']:.0f}/100")
    
    with col3:
        st.metric("Complexity", f"{100 - review_data['complexity_score']:.0f}/100")
    
    with col4:
        st.metric("Issues Found", len(review_data['issues']))
    
    st.divider()
    
    # Tabs for results
    tab1, tab2, tab3, tab4 = st.tabs(["Issues", "Suggestions", "Metrics", "Download"])
    
    with tab1:
        if review_data['issues']:
            for issue in review_data['issues']:
                severity = issue.get('severity', 'low').upper()
                severity_color = {'CRITICAL': '🔴', 'HIGH': '🟠', 'MEDIUM': '🟡', 'LOW': '🟢'}.get(severity, '⚪')
                
                with st.expander(f"{severity_color} {issue.get('type', 'Unknown')} - {issue.get('description', '')[:50]}"):
                    st.write(f"**Category:** {issue.get('category', 'N/A')}")
                    st.write(f"**Severity:** {severity}")
                    if issue.get('line'):
                        st.write(f"**Line:** {issue['line']}")
                    st.write(f"**Description:** {issue.get('description', 'N/A')}")
                    st.write(f"**Suggestion:** {issue.get('suggestion', 'N/A')}")
                    
                    if issue.get('fixed_code'):
                        st.code(issue['fixed_code'], language=review_data.get('language', 'text'))
        else:
            st.success("✅ No significant issues found!")
    
    with tab2:
        if review_data.get('suggestions'):
            for suggestion in review_data['suggestions']:
                with st.expander(f"💡 {suggestion.get('title', 'Suggestion')}"):
                    st.write(f"**Category:** {suggestion.get('category', 'N/A')}")
                    st.write(f"**Priority:** {suggestion.get('priority', 'medium').upper()}")
                    st.write(suggestion.get('description', ''))
                    st.write(f"**Impact:** {suggestion.get('impact', '')}")
        else:
            st.info("No additional suggestions at this time")
    
    with tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Code Metrics**")
            metrics = review_data.get('code_metrics', {})
            st.write(f"Total Lines: {metrics.get('total_lines', 0)}")
            st.write(f"Code Lines: {metrics.get('code_lines', 0)}")
            st.write(f"Comment Lines: {metrics.get('comment_lines', 0)}")
            st.write(f"Avg Line Length: {metrics.get('avg_line_length', 0):.1f}")
        
        with col2:
            st.write("**Complexity Analysis**")
            st.write(f"Analysis Time: {review_data.get('analysis_time', 0):.2f}s")
    
    with tab4:
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📄 Generate HTML Report"):
                html_path = report_generator.generate_html_report(review_data)
                st.success(f"Report saved to {html_path}")
                
                with open(html_path, 'r') as f:
                    st.download_button(
                        label="Download HTML Report",
                        data=f.read(),
                        file_name=os.path.basename(html_path),
                        mime="text/html"
                    )
        
        with col2:
            if st.button("📋 Generate JSON Report"):
                json_path = report_generator.generate_json_report(review_data)
                st.success(f"Report saved to {json_path}")
                
                with open(json_path, 'r') as f:
                    st.download_button(
                        label="Download JSON Report",
                        data=f.read(),
                        file_name=os.path.basename(json_path),
                        mime="application/json"
                    )


def show_history_page():
    """Display review history."""
    st.title("📚 Review History")
    
    if not st.session_state.user:
        st.warning("Please login to view your review history")
        return
    
    reviews = db.get_user_reviews(st.session_state.user['id'])
    
    if not reviews:
        st.info("No reviews yet. Start by reviewing some code!")
    else:
        for review in reviews:
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.write(f"**{review['filename']}**")
            
            with col2:
                st.write(f"Language: {review['language'].upper()}")
            
            with col3:
                st.write(f"Quality: {review['quality_score']:.0f}")
            
            with col4:
                st.write(f"Security: {review['security_score']:.0f}")
            
            with col5:
                st.write(f"Issues: {review['issues_count']}")
            
            st.caption(review['created_at'])
            st.divider()


def show_settings_page():
    """Display settings page."""
    st.title("⚙️ Settings")
    
    if not st.session_state.user:
        st.warning("Please login to access settings")
        return
    
    st.subheader("👤 Profile")
    st.write(f"**Username:** {st.session_state.user['username']}")
    st.write(f"**Email:** {st.session_state.user['email']}")
    st.write(f"**Joined:** {st.session_state.user['created_at']}")
    
    st.divider()
    
    st.subheader("🔑 API Keys")
    
    saved_token = db.get_github_token(st.session_state.user['id'])
    github_token = st.text_input(
        "GitHub Personal Access Token",
        value=saved_token or "",
        type="password",
        help="Get from https://github.com/settings/tokens"
    )
    
    if st.button("Save GitHub Token"):
        if github_token:
            if db.save_github_token(st.session_state.user['id'], github_token):
                st.session_state.github_token = github_token
                st.success("GitHub token saved successfully.")
            else:
                st.error("Unable to save GitHub token. Please try again.")
        else:
            st.error("Please enter a GitHub token before saving.")
    
    if saved_token:
        st.info("A GitHub token is already saved for this account.")
    
    st.divider()
    
    st.subheader("🎨 Preferences")
    
    dark_mode = st.checkbox("Dark Mode", value=False)
    notifications = st.checkbox("Enable Notifications", value=True)
    
    if st.button("Save Preferences"):
        st.success("Preferences saved")


# Main app
def main():
    show_sidebar()
    
    if not st.session_state.user:
        show_login_page()
    else:
        if st.session_state.current_page == 'home':
            show_home_page()
        elif st.session_state.current_page == 'review':
            show_review_page()
        elif st.session_state.current_page == 'history':
            show_history_page()
        elif st.session_state.current_page == 'settings':
            show_settings_page()


if __name__ == "__main__":
    main()