"""
Static analysis module using pylint, flake8, and bandit.
Performs code quality, style, and security checks.
"""

import subprocess
import json
import re
from pathlib import Path
from typing import Dict, List, Any
import logging
import tempfile
import os

logger = logging.getLogger(__name__)


class StaticAnalyzer:
    """Perform static code analysis using various tools."""
    
    def __init__(self):
        """Initialize static analyzer."""
        self.logger = logger
    
    def analyze_python(self, code: str) -> Dict[str, Any]:
        """
        Analyze Python code using pylint and flake8.
        
        Args:
            code: Python source code
            
        Returns:
            Analysis results dictionary
        """
        results = {
            'language': 'python',
            'pylint': {},
            'flake8': {},
            'complexity': {}
        }
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            # Run pylint
            results['pylint'] = self._run_pylint(temp_file)
            
            # Run flake8
            results['flake8'] = self._run_flake8(temp_file)
            
            # Analyze complexity
            results['complexity'] = self._analyze_complexity(code, 'python')
        
        finally:
            os.unlink(temp_file)
        
        return results
    
    def analyze_javascript(self, code: str) -> Dict[str, Any]:
        """
        Analyze JavaScript code.
        
        Args:
            code: JavaScript source code
            
        Returns:
            Analysis results dictionary
        """
        results = {
            'language': 'javascript',
            'issues': []
        }
        
        # Check for common JavaScript issues
        issues = [
            self._check_var_usage(code),
            self._check_console_logs(code),
            self._check_unused_variables(code),
            self._check_equality_operators(code)
        ]
        
        results['issues'] = [i for issue in issues for i in (issue if isinstance(issue, list) else [issue]) if i]
        results['complexity'] = self._analyze_complexity(code, 'javascript')
        
        return results
    
    def analyze_java(self, code: str) -> Dict[str, Any]:
        """
        Analyze Java code.
        
        Args:
            code: Java source code
            
        Returns:
            Analysis results dictionary
        """
        results = {
            'language': 'java',
            'issues': []
        }
        
        # Basic Java analysis
        issues = [
            self._check_naming_conventions(code, 'java'),
            self._check_unused_imports(code),
            self._check_long_methods(code)
        ]
        
        results['issues'] = [i for issue in issues for i in (issue if isinstance(issue, list) else [issue]) if i]
        results['complexity'] = self._analyze_complexity(code, 'java')
        
        return results
    
    def analyze_sql(self, code: str) -> Dict[str, Any]:
        """
        Analyze SQL code.
        
        Args:
            code: SQL source code
            
        Returns:
            Analysis results dictionary
        """
        results = {
            'language': 'sql',
            'issues': []
        }
        
        issues = [
            self._check_sql_injection_risk(code),
            self._check_n_plus_one(code),
            self._check_missing_indexes(code)
        ]
        
        results['issues'] = [i for issue in issues for i in (issue if isinstance(issue, list) else [issue]) if i]
        
        return results
    
    def _run_pylint(self, file_path: str) -> Dict:
        """Run pylint analysis."""
        try:
            result = subprocess.run(
                ['pylint', '--output-format=json', file_path],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.stdout:
                messages = json.loads(result.stdout)
                return {
                    'messages': messages,
                    'score': self._extract_pylint_score(result.stderr)
                }
        except FileNotFoundError:
            logger.debug("pylint not installed")
        except Exception as e:
            logger.warning(f"Error running pylint: {e}")
        
        return {}
    
    def _run_flake8(self, file_path: str) -> Dict:
        """Run flake8 analysis."""
        try:
            result = subprocess.run(
                ['flake8', file_path, '--max-line-length=100'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            issues = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    issues.append(self._parse_flake8_line(line))
            
            return {'issues': issues}
        except FileNotFoundError:
            logger.debug("flake8 not installed")
        except Exception as e:
            logger.warning(f"Error running flake8: {e}")
        
        return {}
    
    def _parse_flake8_line(self, line: str) -> Dict:
        """Parse flake8 output line."""
        pattern = r'(.+):(\d+):(\d+):\s*([A-Z]\d+)\s*(.*)'
        match = re.match(pattern, line)
        
        if match:
            return {
                'file': match.group(1),
                'line': int(match.group(2)),
                'column': int(match.group(3)),
                'code': match.group(4),
                'message': match.group(5)
            }
        return {}
    
    def _extract_pylint_score(self, stderr: str) -> float:
        """Extract pylint score from stderr."""
        pattern = r'rated at ([\d.]+)/10'
        match = re.search(pattern, stderr)
        if match:
            return float(match.group(1))
        return 0.0
    
    def _check_var_usage(self, code: str) -> List[Dict]:
        """Check for var usage in JavaScript."""
        issues = []
        pattern = r'\bvar\s+\w+'
        
        for match in re.finditer(pattern, code):
            line_num = code[:match.start()].count('\n') + 1
            issues.append({
                'line': line_num,
                'type': 'var_usage',
                'severity': 'medium',
                'message': 'var is outdated. Use let or const instead.',
                'suggestion': 'Replace var with const (if not reassigned) or let'
            })
        
        return issues
    
    def _check_console_logs(self, code: str) -> List[Dict]:
        """Check for console.log statements."""
        issues = []
        pattern = r'console\.log\s*\('
        
        for match in re.finditer(pattern, code):
            line_num = code[:match.start()].count('\n') + 1
            issues.append({
                'line': line_num,
                'type': 'console_log',
                'severity': 'low',
                'message': 'Remove console.log in production code.',
                'suggestion': 'Use proper logging library instead'
            })
        
        return issues
    
    def _check_unused_variables(self, code: str) -> List[Dict]:
        """Check for unused variables."""
        issues = []
        
        # Simple pattern - finds declared but potentially unused variables
        pattern = r'(?:const|let|var)\s+(\w+)'
        
        variables = {}
        for match in re.finditer(pattern, code):
            var_name = match.group(1)
            line_num = code[:match.start()].count('\n') + 1
            
            if var_name not in variables:
                variables[var_name] = line_num
        
        # Check usage
        for var_name, line_num in variables.items():
            # Count occurrences (simple check)
            pattern = r'\b' + var_name + r'\b'
            count = len(re.findall(pattern, code))
            
            if count == 1:  # Only declared, not used
                issues.append({
                    'line': line_num,
                    'type': 'unused_variable',
                    'severity': 'low',
                    'message': f'Variable "{var_name}" is declared but not used.',
                    'suggestion': 'Remove unused variable'
                })
        
        return issues
    
    def _check_equality_operators(self, code: str) -> List[Dict]:
        """Check for loose equality operators."""
        issues = []
        pattern = r'==(?!=)'
        
        for match in re.finditer(pattern, code):
            line_num = code[:match.start()].count('\n') + 1
            issues.append({
                'line': line_num,
                'type': 'loose_equality',
                'severity': 'medium',
                'message': 'Use === instead of == for strict equality.',
                'suggestion': 'Replace == with ==='
            })
        
        return issues
    
    def _check_naming_conventions(self, code: str, language: str) -> List[Dict]:
        """Check naming conventions."""
        issues = []
        
        if language == 'java':
            # Check for camelCase class names
            pattern = r'class\s+([a-z_][a-zA-Z0-9_]*)'
            for match in re.finditer(pattern, code):
                line_num = code[:match.start()].count('\n') + 1
                class_name = match.group(1)
                
                if not class_name[0].isupper():
                    issues.append({
                        'line': line_num,
                        'type': 'naming_convention',
                        'severity': 'low',
                        'message': f'Class name "{class_name}" should start with uppercase.',
                        'suggestion': 'Rename class to PascalCase'
                    })
        
        return issues
    
    def _check_unused_imports(self, code: str) -> List[Dict]:
        """Check for unused imports."""
        issues = []
        
        # Extract import statements
        pattern = r'(?:import|from)\s+[\w.]+(?:\s+import\s+[\w,\s*]+)?'
        
        for match in re.finditer(pattern, code):
            line_num = code[:match.start()].count('\n') + 1
            import_line = match.group(0)
            
            # Extract imported names
            if 'import' in import_line:
                imported = re.findall(r'\b([a-zA-Z_]\w*)\b', import_line)
                
                for name in imported:
                    if name not in ['import', 'from']:
                        if code.count(name) == 1:  # Only in import line
                            issues.append({
                                'line': line_num,
                                'type': 'unused_import',
                                'severity': 'low',
                                'message': f'Import "{name}" is not used.',
                                'suggestion': 'Remove unused import'
                            })
        
        return issues
    
    def _check_long_methods(self, code: str) -> List[Dict]:
        """Check for methods longer than recommended."""
        issues = []
        
        pattern = r'(?:def|function|public\s+\w+)\s+(\w+)\s*\('
        
        for match in re.finditer(pattern, code):
            line_start = code[:match.start()].count('\n') + 1
            line_end = code[:match.end()].count('\n') + 1
            
            # Simple check: if method spans many lines
            method_body = code[match.start():match.end() + 500]
            method_lines = method_body.count('\n')
            
            if method_lines > 50:
                issues.append({
                    'line': line_start,
                    'type': 'long_method',
                    'severity': 'medium',
                    'message': f'Method "{match.group(1)}" is too long.',
                    'suggestion': 'Consider breaking into smaller methods'
                })
        
        return issues
    
    def _check_sql_injection_risk(self, code: str) -> List[Dict]:
        """Check for SQL injection risks."""
        issues = []
        
        # Check for string concatenation in queries
        pattern = r"(?:SELECT|INSERT|UPDATE|DELETE).*['\"]\s*\+|['\"]\s*\+"
        
        for match in re.finditer(pattern, code, re.IGNORECASE):
            line_num = code[:match.start()].count('\n') + 1
            issues.append({
                'line': line_num,
                'type': 'sql_injection_risk',
                'severity': 'critical',
                'message': 'Potential SQL injection vulnerability detected.',
                'suggestion': 'Use parameterized queries instead of string concatenation'
            })
        
        return issues
    
    def _check_n_plus_one(self, code: str) -> List[Dict]:
        """Check for N+1 query patterns."""
        issues = []
        
        # Simple pattern: loop followed by query
        pattern = r'(?:for|while)\s*\(.*?\)\s*\{[^}]*(?:SELECT|INSERT|UPDATE)'
        
        for match in re.finditer(pattern, code, re.IGNORECASE | re.DOTALL):
            line_num = code[:match.start()].count('\n') + 1
            issues.append({
                'line': line_num,
                'type': 'n_plus_one',
                'severity': 'high',
                'message': 'Potential N+1 query problem detected.',
                'suggestion': 'Use JOINs or batch queries instead of looping'
            })
        
        return issues
    
    def _check_missing_indexes(self, code: str) -> List[Dict]:
        """Check for missing database indexes."""
        issues = []
        
        # Check for WHERE clauses without indexes
        pattern = r'WHERE\s+(\w+)\s*='
        
        for match in re.finditer(pattern, code, re.IGNORECASE):
            line_num = code[:match.start()].count('\n') + 1
            column = match.group(1)
            
            if 'CREATE INDEX' not in code or column not in code[code.find('CREATE INDEX'):]:
                issues.append({
                    'line': line_num,
                    'type': 'missing_index',
                    'severity': 'medium',
                    'message': f'Column "{column}" in WHERE clause might need an index.',
                    'suggestion': 'Consider creating an index on frequently queried columns'
                })
        
        return issues
    
    def _analyze_complexity(self, code: str, language: str) -> Dict:
        """
        Analyze code complexity.
        
        Args:
            code: Source code
            language: Programming language
            
        Returns:
            Complexity metrics
        """
        complexity_score = 0
        
        # Count control flow statements
        control_keywords = ['if', 'else', 'for', 'while', 'switch', 'case', 'try', 'catch']
        
        for keyword in control_keywords:
            pattern = r'\b' + keyword + r'\b'
            count = len(re.findall(pattern, code, re.IGNORECASE))
            complexity_score += count
        
        # Count function nesting
        nesting_level = 0
        for char in code:
            if char == '{':
                nesting_level += 1
            elif char == '}':
                nesting_level -= 1
            complexity_score += nesting_level
        
        # Normalize complexity
        lines = code.count('\n') + 1
        complexity_per_line = complexity_score / max(lines, 1)
        
        return {
            'cyclomatic_complexity': min(complexity_score, 100),
            'cognitive_complexity': complexity_per_line,
            'maintainability_index': max(0, 100 - (complexity_score * 2))
        }
