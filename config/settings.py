"""
Configuration settings for the AI Code Reviewer application.
Manages environment variables and application configuration.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Application settings
APP_NAME = "AI Code Reviewer"
APP_VERSION = "1.0.0"
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Database settings
DATABASE_PATH = os.getenv("DATABASE_PATH", str(BASE_DIR / "code_reviewer.db"))

# Server settings
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8501"))

# File upload settings
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "1048576"))  # 1MB default
UPLOAD_DIR = os.getenv("UPLOAD_DIR", str(BASE_DIR / "uploads"))
REPORTS_DIR = os.getenv("REPORTS_DIR", str(BASE_DIR / "reports"))

# Analysis settings
MAX_CODE_LENGTH = int(os.getenv("MAX_CODE_LENGTH", "1000000"))  # 1MB
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "5000"))  # Characters per chunk
ANALYSIS_TIMEOUT = int(os.getenv("ANALYSIS_TIMEOUT", "30"))  # Seconds

# Security settings
SECRET_KEY = os.getenv("SECRET_KEY", "change-this-in-production")
PASSWORD_MIN_LENGTH = int(os.getenv("PASSWORD_MIN_LENGTH", "6"))

# GitHub API settings
GITHUB_API_BASE = "https://api.github.com"
GITHUB_API_TIMEOUT = int(os.getenv("GITHUB_API_TIMEOUT", "10"))

# Rate limiting
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "3600"))  # 1 hour

# Logging settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = os.getenv("LOG_FILE", str(BASE_DIR / "code_reviewer.log"))

# Supported languages and their extensions
SUPPORTED_LANGUAGES = {
    "python": [".py"],
    "javascript": [".js", ".jsx", ".mjs"],
    "typescript": [".ts", ".tsx"],
    "java": [".java"],
    "c": [".c", ".h"],
    "cpp": [".cpp", ".cc", ".cxx", ".h", ".hpp"],
    "csharp": [".cs"],
    "go": [".go"],
    "rust": [".rs"],
    "php": [".php"],
    "ruby": [".rb"],
    "sql": [".sql"],
    "html": [".html", ".htm", ".xhtml"],
    "css": [".css", ".scss", ".sass", ".less"],
    "json": [".json"],
    "xml": [".xml"],
    "yaml": [".yml", ".yaml"],
    "shell": [".sh", ".bash", ".zsh"],
}

# Severity levels
SEVERITY_LEVELS = ["critical", "high", "medium", "low"]

# Score weights for overall calculation
SCORE_WEIGHTS = {
    "quality": 0.4,
    "security": 0.4,
    "complexity": 0.2,
}

# Directories to ignore when analyzing projects
IGNORED_DIRECTORIES = [
    ".git",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
    ".tox",
    "build",
    "dist",
    ".idea",
    ".vscode",
    "coverage",
    ".nyc_output",
    "target",
    ".gradle",
    "bin",
    "obj",
]

# File patterns to ignore
IGNORED_FILE_PATTERNS = [
    "*.pyc",
    "*.pyo",
    "*.so",
    "*.dll",
    "*.exe",
    "*.class",
    "*.jar",
    "*.war",
    "*.zip",
    "*.tar",
    "*.gz",
    "*.min.js",
    "*.bundle.js",
    "*.lock",
]

# Create necessary directories
def initialize_directories():
    """Create necessary directories if they don't exist."""
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)

# Initialize on module load
initialize_directories()


def get_setting(key, default=None):
    """
    Get a setting value from environment or return default.
    
    Args:
        key: Setting key
        default: Default value if not found
        
    Returns:
        Setting value
    """
    return os.getenv(key, default)


def is_language_supported(language):
    """
    Check if a programming language is supported.
    
    Args:
        language: Language name
        
    Returns:
        True if supported, False otherwise
    """
    return language.lower() in SUPPORTED_LANGUAGES


def get_extensions_for_language(language):
    """
    Get file extensions for a programming language.
    
    Args:
        language: Language name
        
    Returns:
        List of file extensions
    """
    return SUPPORTED_LANGUAGES.get(language.lower(), [])


def should_ignore_file(filepath):
    """
    Check if a file should be ignored during analysis.
    
    Args:
        filepath: Path to the file
        
    Returns:
        True if should be ignored, False otherwise
    """
    filepath = str(filepath).lower()
    
    # Check directory
    for ignored_dir in IGNORED_DIRECTORIES:
        if f"/{ignored_dir}/" in filepath or filepath.startswith(f"{ignored_dir}/"):
            return True
    
    # Check file patterns
    for pattern in IGNORED_FILE_PATTERNS:
        if filepath.endswith(pattern.replace("*", "")):
            return True
    
    return False