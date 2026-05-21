"""
Database module for managing SQLite operations.
Handles user authentication, review history, and report storage.
Thread-safe implementation for Streamlit.
"""

import sqlite3
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
import logging
import threading

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages SQLite database operations for the code reviewer application."""
    
    def __init__(self, db_path: str = None):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        if db_path is None:
            repo_root = Path(__file__).resolve().parent.parent
            db_path = repo_root / "code_reviewer.db"
        
        self.db_path = str(db_path)
        self._local = threading.local()  # Thread-local storage for connections
        self.initialize_db()
        logger.info(f"DatabaseManager initialized with path: {self.db_path}")
    
    def get_connection(self):
        """Get or create database connection for current thread (thread-safe)."""
        if not hasattr(self._local, 'connection') or self._local.connection is None:
            self._local.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self._local.connection.row_factory = sqlite3.Row
            logger.debug(f"Created new database connection for thread {threading.current_thread().ident}")
        return self._local.connection
    
    def initialize_db(self):
        """Create all required tables if they don't exist."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            """)
            
            # Reviews table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reviews (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    filename TEXT NOT NULL,
                    language TEXT NOT NULL,
                    file_size INTEGER,
                    code_content TEXT,
                    review_result TEXT,
                    quality_score REAL,
                    security_score REAL,
                    issues_count INTEGER,
                    analysis_time REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            
            # Review Issues table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS review_issues (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    review_id INTEGER NOT NULL,
                    issue_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    line_number INTEGER,
                    description TEXT NOT NULL,
                    suggestion TEXT,
                    fixed_code TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (review_id) REFERENCES reviews(id) ON DELETE CASCADE
                )
            """)
            
            # Saved Reports table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS saved_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    review_id INTEGER NOT NULL,
                    report_title TEXT NOT NULL,
                    report_path TEXT,
                    report_format TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (review_id) REFERENCES reviews(id) ON DELETE CASCADE
                )
            """)
            
            # GitHub repos table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS github_repos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    repo_name TEXT NOT NULL,
                    repo_url TEXT NOT NULL,
                    last_analyzed TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            
            # GitHub token storage table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS github_tokens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL UNIQUE,
                    token TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            
            conn.commit()
            logger.info("Database initialized successfully with all tables")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def hash_password(self, password: str) -> str:
        """
        Hash password using SHA256.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str, stored_hash: str) -> bool:
        """
        Verify a password against a stored hash.
        
        Args:
            password: Plain text password to verify
            stored_hash: The hash to compare against
            
        Returns:
            True if password matches, False otherwise
        """
        return self.hash_password(password) == stored_hash
    
    def register_user(self, username: str, email: str, password: str) -> bool:
        """
        Register a new user.
        
        Args:
            username: Username
            email: User email
            password: Plain text password
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            password_hash = self.hash_password(password)
            
            logger.debug(f"Attempting to register user: {username}, email: {email}")
            
            cursor.execute("""
                INSERT INTO users (username, email, password_hash)
                VALUES (?, ?, ?)
            """, (username, email, password_hash))
            
            conn.commit()
            logger.info(f"User registered successfully: {username}")
            return True
        except sqlite3.IntegrityError as e:
            logger.error(f"Registration error - user/email already exists: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error registering user: {e}")
            return False
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """
        Authenticate user credentials.
        
        Args:
            username: Username
            password: Plain text password
            
        Returns:
            User data dict if successful, None otherwise
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            logger.debug(f"Attempting to authenticate user: {username}")
            
            # First, check if user exists
            cursor.execute("""
                SELECT id, username, email, password_hash, created_at, is_active
                FROM users 
                WHERE username = ? AND is_active = 1
            """, (username,))
            
            user = cursor.fetchone()
            
            if user is None:
                logger.warning(f"Authentication failed - user not found: {username}")
                return None
            
            user_dict = dict(user)
            stored_hash = user_dict['password_hash']
            
            # Verify password
            if not self.verify_password(password, stored_hash):
                logger.warning(f"Authentication failed - incorrect password for user: {username}")
                return None
            
            # Remove password_hash from returned data
            del user_dict['password_hash']
            
            logger.info(f"User authenticated successfully: {username}")
            return user_dict
            
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """
        Get user by username (for debugging).
        
        Args:
            username: Username
            
        Returns:
            User data dict if found, None otherwise
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, username, email, created_at, is_active
                FROM users 
                WHERE username = ?
            """, (username,))
            
            user = cursor.fetchone()
            if user:
                return dict(user)
            return None
        except Exception as e:
            logger.error(f"Error getting user by username: {e}")
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User data dict if found, None otherwise
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, username, email, created_at 
                FROM users 
                WHERE id = ? AND is_active = 1
            """, (user_id,))
            
            user = cursor.fetchone()
            if user:
                return dict(user)
            return None
        except Exception as e:
            logger.error(f"Error getting user by id: {e}")
            return None
    
    def get_all_users(self) -> List[Dict]:
        """
        Get all users (for debugging).
        
        Returns:
            List of all users
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, username, email, created_at, is_active
                FROM users
                ORDER BY created_at DESC
            """)
            
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []
    
    def save_github_token(self, user_id: int, token: str) -> bool:
        """
        Save or update a user's GitHub personal access token.
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO github_tokens (user_id, token)
                VALUES (?, ?)
                ON CONFLICT(user_id) DO UPDATE SET token = excluded.token,
                    updated_at = CURRENT_TIMESTAMP
            """, (user_id, token))
            conn.commit()
            logger.info(f"Saved GitHub token for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error saving GitHub token: {e}")
            return False
    
    def get_github_token(self, user_id: int) -> Optional[str]:
        """
        Retrieve a saved GitHub token for a user.
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT token
                FROM github_tokens
                WHERE user_id = ?
            """, (user_id,))
            row = cursor.fetchone()
            return row['token'] if row else None
        except Exception as e:
            logger.error(f"Error retrieving GitHub token: {e}")
            return None
    
    def save_review(self, user_id: int, filename: str, language: str, 
                   file_size: int, code_content: str, review_result: str,
                   quality_score: float, security_score: float, 
                   issues_count: int, analysis_time: float) -> int:
        """
        Save a code review to database.
        
        Args:
            user_id: User ID
            filename: Original filename
            language: Programming language
            file_size: File size in bytes
            code_content: Source code
            review_result: JSON review result
            quality_score: Code quality score (0-100)
            security_score: Security score (0-100)
            issues_count: Number of issues found
            analysis_time: Time taken for analysis
            
        Returns:
            Review ID
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO reviews 
                (user_id, filename, language, file_size, code_content, 
                 review_result, quality_score, security_score, issues_count, 
                 analysis_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, filename, language, file_size, code_content,
                  review_result, quality_score, security_score, 
                  issues_count, analysis_time))
            
            conn.commit()
            review_id = cursor.lastrowid
            logger.info(f"Review saved: {review_id}")
            return review_id
        except Exception as e:
            logger.error(f"Error saving review: {e}")
            return -1
    
    def save_review_issues(self, review_id: int, issues: List[Dict]) -> bool:
        """
        Save individual review issues.
        
        Args:
            review_id: Review ID
            issues: List of issue dictionaries
            
        Returns:
            True if successful
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            for issue in issues:
                cursor.execute("""
                    INSERT INTO review_issues 
                    (review_id, issue_type, severity, line_number, 
                     description, suggestion, fixed_code)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    review_id,
                    issue.get('type', 'Unknown'),
                    issue.get('severity', 'Low'),
                    issue.get('line', 0),
                    issue.get('description', ''),
                    issue.get('suggestion', ''),
                    issue.get('fixed_code', '')
                ))
            
            conn.commit()
            logger.info(f"Saved {len(issues)} issues for review {review_id}")
            return True
        except Exception as e:
            logger.error(f"Error saving review issues: {e}")
            return False
    
    def get_user_reviews(self, user_id: int, limit: int = 50) -> List[Dict]:
        """
        Get all reviews for a user.
        
        Args:
            user_id: User ID
            limit: Maximum number of reviews to return
            
        Returns:
            List of review dictionaries
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, filename, language, quality_score, security_score,
                       issues_count, created_at
                FROM reviews
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (user_id, limit))
            
            reviews = [dict(row) for row in cursor.fetchall()]
            return reviews
        except Exception as e:
            logger.error(f"Error retrieving user reviews: {e}")
            return []
    
    def get_review_details(self, review_id: int) -> Optional[Dict]:
        """
        Get detailed review information.
        
        Args:
            review_id: Review ID
            
        Returns:
            Review details dict
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, user_id, filename, language, quality_score, 
                       security_score, issues_count, review_result, 
                       code_content, analysis_time, created_at
                FROM reviews
                WHERE id = ?
            """, (review_id,))
            
            review = cursor.fetchone()
            if review:
                review_dict = dict(review)
                
                # Get issues
                cursor.execute("""
                    SELECT issue_type, severity, line_number, description, 
                           suggestion, fixed_code
                    FROM review_issues
                    WHERE review_id = ?
                    ORDER BY severity DESC, line_number ASC
                """, (review_id,))
                
                review_dict['issues'] = [dict(row) for row in cursor.fetchall()]
                return review_dict
            return None
        except Exception as e:
            logger.error(f"Error retrieving review details: {e}")
            return None
    
    def close(self):
        """Close all database connections."""
        if hasattr(self._local, 'connection') and self._local.connection:
            self._local.connection.close()
            self._local.connection = None
            logger.debug("Database connection closed")


# Singleton instance
_db_instance = None
_db_lock = threading.Lock()


def get_db() -> DatabaseManager:
    """Get or create database instance (thread-safe singleton)."""
    global _db_instance
    if _db_instance is None:
        with _db_lock:
            if _db_instance is None:
                _db_instance = DatabaseManager()
    return _db_instance