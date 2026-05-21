"""Code Reviewer Package"""

__version__ = '1.0.0'
__author__ = 'AI Code Reviewer Team'
__description__ = 'AI-Powered Automated Code Reviewer'

from database.db import get_db
from utils.code_parser import CodeParser
from utils.static_analyzer import StaticAnalyzer
from utils.security_checker import SecurityChecker
from utils.report_generator import ReportGenerator
from utils.github_fetcher import GitHubFetcher
from models.ai_reviewer import AIReviewer

__all__ = [
    'get_db',
    'CodeParser',
    'StaticAnalyzer',
    'SecurityChecker',
    'ReportGenerator',
    'GitHubFetcher',
    'AIReviewer'
]
