"""
Unit tests for Code Reviewer modules.
Test code parser, static analyzer, security checker, and AI reviewer.
"""

import unittest
from pathlib import Path
import tempfile
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.code_parser import CodeParser
from utils.static_analyzer import StaticAnalyzer
from utils.security_checker import SecurityChecker
from utils.github_fetcher import GitHubFetcher
from models.ai_reviewer import AIReviewer
from database.db import DatabaseManager


class TestCodeParser(unittest.TestCase):
    """Test CodeParser module."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = CodeParser()
    
    def test_language_detection_python(self):
        """Test Python language detection."""
        filename = "test.py"
        language = self.parser.detect_language(filename)
        self.assertEqual(language, 'python')
    
    def test_language_detection_javascript(self):
        """Test JavaScript language detection."""
        filename = "test.js"
        language = self.parser.detect_language(filename)
        self.assertEqual(language, 'javascript')
    
    def test_language_detection_java(self):
        """Test Java language detection."""
        filename = "Test.java"
        language = self.parser.detect_language(filename)
        self.assertEqual(language, 'java')
    
    def test_language_detection_by_content(self):
        """Test language detection by content."""
        python_code = "def hello():\n    print('hello')"
        language = self.parser.detect_language("code", python_code)
        self.assertEqual(language, 'python')
    
    def test_extract_functions_python(self):
        """Test function extraction from Python code."""
        code = """
def hello(name):
    return f'Hello {name}'

def add(a, b):
    return a + b
"""
        functions = self.parser.extract_functions(code, 'python')
        self.assertEqual(len(functions), 2)
        self.assertEqual(functions[0]['name'], 'hello')
    
    def test_code_metrics(self):
        """Test code metrics calculation."""
        code = "def hello():\n    pass\n\ndef world():\n    pass\n"
        metrics = self.parser.get_code_metrics(code)
        
        self.assertIn('total_lines', metrics)
        self.assertIn('code_lines', metrics)
        self.assertGreater(metrics['total_lines'], 0)
    
    def test_code_validation(self):
        """Test code validation."""
        valid_code = "print('hello')"
        is_valid, msg = self.parser.validate_code(valid_code, 'python')
        self.assertTrue(is_valid)
        
        invalid_code = ""
        is_valid, msg = self.parser.validate_code(invalid_code, 'python')
        self.assertFalse(is_valid)
    
    def test_clean_code(self):
        """Test code cleaning."""
        dirty_code = "def hello():  \n    pass  \n\n\n"
        clean = self.parser.clean_code(dirty_code)
        self.assertNotIn('  \n', clean)


class TestSecurityChecker(unittest.TestCase):
    """Test SecurityChecker module."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.checker = SecurityChecker()
    
    def test_sql_injection_detection(self):
        """Test SQL injection vulnerability detection."""
        code = "query = 'SELECT * FROM users WHERE id = ' + user_input"
        results = self.checker.check_security(code, 'python')
        self.assertGreater(len(results['vulnerabilities']), 0)
    
    def test_hardcoded_secret_detection(self):
        """Test hardcoded secret detection."""
        code = 'api_key = "sk_live_123456789"'
        results = self.checker.check_security(code, 'python')
        self.assertGreater(len(results['secrets_found']), 0)
    
    def test_eval_detection(self):
        """Test unsafe eval() detection."""
        code = "result = eval(user_input)"
        results = self.checker.check_security(code, 'python')
        self.assertGreater(len(results['unsafe_functions']), 0)
    
    def test_command_injection_detection(self):
        """Test command injection detection."""
        code = "os.system('rm -rf ' + user_path)"
        results = self.checker.check_security(code, 'python')
        self.assertGreater(len(results['vulnerabilities']), 0)
    
    def test_security_score_calculation(self):
        """Test security score calculation."""
        code = "safe_code = print('hello')"
        results = self.checker.check_security(code, 'python')
        self.assertGreaterEqual(results['security_score'], 0)
        self.assertLessEqual(results['security_score'], 100)


class TestAIReviewer(unittest.TestCase):
    """Test AIReviewer module."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.reviewer = AIReviewer()
    
    def test_review_code_basic(self):
        """Test basic code review."""
        code = "def hello():\n    pass"
        review = self.reviewer.review_code(code, 'python', {})
        
        self.assertIn('quality_score', review)
        self.assertIn('security_score', review)
        self.assertIn('issues', review)
    
    def test_quality_score_calculation(self):
        """Test quality score calculation."""
        code = "def hello():\n    pass"
        review = self.reviewer.review_code(code, 'python', {})
        
        self.assertGreaterEqual(review['quality_score'], 0)
        self.assertLessEqual(review['quality_score'], 100)
    
    def test_issue_detection(self):
        """Test issue detection in code."""
        code = "except:\n    pass"  # Bare except
        review = self.reviewer.review_code(code, 'python', {})
        
        # Should detect bare except issue
        self.assertGreater(len(review['issues']), 0)


class TestStaticAnalyzer(unittest.TestCase):
    """Test StaticAnalyzer module."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = StaticAnalyzer()
    
    def test_javascript_analysis(self):
        """Test JavaScript analysis."""
        code = """
var x = 5;
console.log(x);
if (x == 5) {
    console.log('equal');
}
"""
        results = self.analyzer.analyze_javascript(code)
        self.assertIn('issues', results)
    
    def test_complexity_analysis(self):
        """Test complexity analysis."""
        code = "if x: pass"
        complexity = self.analyzer._analyze_complexity(code, 'python')
        self.assertIn('cyclomatic_complexity', complexity)
        self.assertIn('maintainability_index', complexity)


class TestDatabaseGitHubToken(unittest.TestCase):
    """Test GitHub token storage in the database."""

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmp_dir.name) / "test_code_reviewer.db"
        self.db = DatabaseManager(str(self.db_path))
        self.db.register_user("testuser", "test@example.com", "password123")
        self.user = self.db.authenticate_user("testuser", "password123")

    def tearDown(self):
        self.db.close()
        self.tmp_dir.cleanup()

    def test_save_and_retrieve_github_token(self):
        saved = self.db.save_github_token(self.user['id'], 'ghp_testtoken123')
        self.assertTrue(saved)
        token = self.db.get_github_token(self.user['id'])
        self.assertEqual(token, 'ghp_testtoken123')


class TestGitHubFetcher(unittest.TestCase):
    """Test GitHub URL parsing helper."""

    def test_parse_repo_url(self):
        fetcher = GitHubFetcher('dummy')
        self.assertEqual(fetcher._parse_repo_url('https://github.com/owner/repo'), ('owner', 'repo'))
        self.assertEqual(fetcher._parse_repo_url('git@github.com:owner/repo.git'), ('owner', 'repo'))


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete review pipeline."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = CodeParser()
        self.checker = SecurityChecker()
        self.reviewer = AIReviewer()
    
    def test_complete_review_pipeline(self):
        """Test complete code review pipeline."""
        code = """
def process_user_input(user_input):
    query = 'SELECT * FROM users WHERE id = ' + user_input
    result = eval(user_input)
    return result
"""
        
        # Detect language
        language = self.parser.detect_language("code.py", code)
        self.assertEqual(language, 'python')
        
        # Security check
        security = self.checker.check_security(code, 'python')
        self.assertGreater(len(security['vulnerabilities']), 0)
        
        # AI Review
        review = self.reviewer.review_code(code, language, {})
        self.assertGreater(len(review['issues']), 0)
        self.assertLess(review['security_score'], 80)


def run_tests():
    """Run all tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add tests
    suite.addTests(loader.loadTestsFromTestCase(TestCodeParser))
    suite.addTests(loader.loadTestsFromTestCase(TestSecurityChecker))
    suite.addTests(loader.loadTestsFromTestCase(TestAIReviewer))
    suite.addTests(loader.loadTestsFromTestCase(TestStaticAnalyzer))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
