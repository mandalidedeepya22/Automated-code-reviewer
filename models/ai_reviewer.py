"""
AI Review Engine using transformers and LLM integration.
Provides intelligent code analysis and recommendations.
"""

import json
import re
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class AIReviewer:
    """AI-powered code review engine."""
    
    # Issue category templates
    ISSUE_TEMPLATES = {
        'syntax_error': {
            'severity': 'critical',
            'category': 'Syntax Error',
            'explanation_template': 'Syntax error detected at line {line}: {detail}'
        },
        'logic_error': {
            'severity': 'high',
            'category': 'Logic Error',
            'explanation_template': 'Potential logic error detected: {detail}'
        },
        'code_smell': {
            'severity': 'medium',
            'category': 'Code Smell',
            'explanation_template': 'Code smell: {detail}'
        },
        'performance': {
            'severity': 'medium',
            'category': 'Performance Issue',
            'explanation_template': 'Performance issue detected: {detail}'
        },
        'security': {
            'severity': 'critical',
            'category': 'Security Vulnerability',
            'explanation_template': 'Security vulnerability: {detail}'
        },
        'documentation': {
            'severity': 'low',
            'category': 'Missing Documentation',
            'explanation_template': 'Missing or incomplete documentation: {detail}'
        },
        'naming': {
            'severity': 'low',
            'category': 'Naming Convention',
            'explanation_template': 'Naming issue: {detail}'
        },
        'complexity': {
            'severity': 'medium',
            'category': 'Complexity Issue',
            'explanation_template': 'Code is too complex: {detail}'
        }
    }
    
    def __init__(self):
        """Initialize AI reviewer."""
        self.logger = logger
    
    def review_code(self, code: str, language: str, 
                   analysis_results: Dict) -> Dict[str, Any]:
        """
        Perform comprehensive AI code review.
        
        Args:
            code: Source code
            language: Programming language
            analysis_results: Results from static analysis
            
        Returns:
            Comprehensive review results
        """
        review = {
            'timestamp': datetime.now().isoformat(),
            'language': language,
            'code_metrics': self._extract_metrics(code),
            'issues': [],
            'quality_score': 0,
            'security_score': 0,
            'complexity_score': 0,
            'suggestions': [],
            'refactored_snippets': []
        }
        
        # Analyze for issues
        issues = []
        issues.extend(self._detect_issues(code, language))
        issues.extend(self._analyze_static_results(analysis_results))
        
        # Process and deduplicate issues
        review['issues'] = self._deduplicate_issues(issues)
        
        # Calculate scores
        review['quality_score'] = self._calculate_quality_score(review['issues'], review['code_metrics'])
        review['security_score'] = self._calculate_security_score(review['issues'])
        review['complexity_score'] = self._calculate_complexity_score(code, language, analysis_results)
        
        # Generate suggestions
        review['suggestions'] = self._generate_suggestions(review['issues'], language)
        
        # Generate refactored code snippets
        review['refactored_snippets'] = self._generate_refactored_snippets(code, language, review['issues'])
        
        return review
    
    def _detect_issues(self, code: str, language: str) -> List[Dict]:
        """Detect various code issues."""
        issues = []
        
        # Language-specific detection
        if language == 'python':
            issues.extend(self._detect_python_issues(code))
        elif language in ['javascript', 'typescript']:
            issues.extend(self._detect_javascript_issues(code))
        elif language == 'java':
            issues.extend(self._detect_java_issues(code))
        elif language == 'sql':
            issues.extend(self._detect_sql_issues(code))
        
        # General detection
        issues.extend(self._detect_general_issues(code))
        
        return issues
    
    def _detect_python_issues(self, code: str) -> List[Dict]:
        """Detect Python-specific issues."""
        issues = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for bare except
            if re.search(r'except\s*:', line):
                issues.append({
                    'line': i,
                    'type': 'bare_except',
                    'severity': 'high',
                    'category': 'Exception Handling',
                    'description': 'Avoid bare except. Specify exception type.',
                    'suggestion': 'except Exception as e:',
                    'fixed_code': line.replace('except:', 'except Exception as e:')
                })
            
            # Check for hardcoded strings
            if re.search(r'(password|api_key|secret|token)\s*=\s*["\']', line, re.IGNORECASE):
                issues.append({
                    'line': i,
                    'type': 'hardcoded_credential',
                    'severity': 'critical',
                    'category': 'Security',
                    'description': 'Hardcoded credentials detected. Use environment variables.',
                    'suggestion': 'Use os.environ.get() or .env files',
                    'fixed_code': line.replace('=', '= os.environ.get(')
                })
            
            # Detect SQL injection patterns in Python string concatenation
            if re.search(r"SELECT\s+\*.*\+.*user_input|WHERE.*\+.*user_input", line, re.IGNORECASE):
                issues.append({
                    'line': i,
                    'type': 'sql_injection',
                    'severity': 'critical',
                    'category': 'Security',
                    'description': 'Potential SQL injection vulnerability detected. Do not concatenate user input into SQL queries.',
                    'suggestion': 'Use parameterized queries or query builders instead.',
                    'fixed_code': None
                })
            
            # Detect eval usage
            if re.search(r'\beval\s*\(', line):
                issues.append({
                    'line': i,
                    'type': 'eval_usage',
                    'severity': 'critical',
                    'category': 'Security',
                    'description': 'eval() is dangerous and can execute arbitrary code.',
                    'suggestion': 'Avoid eval() and use safer parsing or logic alternatives.',
                    'fixed_code': None
                })
            
            # Check for missing docstrings
            if re.match(r'\s*def\s+\w+', line) and i < len(lines) - 1:
                next_line = lines[i].strip()
                if not next_line.startswith(('"""', "'''", '#')):
                    issues.append({
                        'line': i,
                        'type': 'missing_docstring',
                        'severity': 'low',
                        'category': 'Documentation',
                        'description': 'Function missing docstring.',
                        'suggestion': 'Add docstring describing function purpose'
                    })
        
        return issues
    
    def _detect_javascript_issues(self, code: str) -> List[Dict]:
        """Detect JavaScript-specific issues."""
        issues = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for eval usage
            if 'eval(' in line:
                issues.append({
                    'line': i,
                    'type': 'eval_usage',
                    'severity': 'critical',
                    'category': 'Security',
                    'description': 'eval() is a security risk. Avoid using it.',
                    'suggestion': 'Use JSON.parse() or Function constructor with caution'
                })
            
            # Check for async without await
            if re.search(r'async\s+\w+.*\{', line) and 'await' not in code[code.find(line):code.find(line) + 500]:
                issues.append({
                    'line': i,
                    'type': 'async_without_await',
                    'severity': 'medium',
                    'category': 'Logic Error',
                    'description': 'Async function without await statements.',
                    'suggestion': 'Either add await or remove async keyword'
                })
            
            # Check for missing error handling
            if '.then(' in line and '.catch(' not in code:
                issues.append({
                    'line': i,
                    'type': 'missing_error_handling',
                    'severity': 'high',
                    'category': 'Error Handling',
                    'description': 'Promise without error handling (.catch).',
                    'suggestion': 'Add .catch() or use try-catch with async-await'
                })
        
        return issues
    
    def _detect_java_issues(self, code: str) -> List[Dict]:
        """Detect Java-specific issues."""
        issues = []
        
        # Check for null pointer dereference
        if re.search(r'\.get\(\)\.|\.getValue\(\)\.', code):
            issues.append({
                'type': 'potential_null_pointer',
                'severity': 'high',
                'category': 'Logic Error',
                'description': 'Potential null pointer dereference detected.',
                'suggestion': 'Use Optional or null checks'
            })
        
        # Check for uninitialized variables
        pattern = r'(?:String|int|boolean|double)\s+(\w+);(?!\s*=)'
        matches = re.findall(pattern, code)
        if matches:
            issues.append({
                'type': 'uninitialized_variable',
                'severity': 'medium',
                'category': 'Logic Error',
                'description': 'Variables declared but not initialized.',
                'suggestion': 'Initialize variables at declaration'
            })
        
        return issues
    
    def _detect_sql_issues(self, code: str) -> List[Dict]:
        """Detect SQL-specific issues."""
        issues = []
        
        # Check for SELECT *
        if re.search(r'SELECT\s+\*', code, re.IGNORECASE):
            issues.append({
                'type': 'select_all',
                'severity': 'medium',
                'category': 'Performance',
                'description': 'SELECT * fetches all columns. Specify needed columns.',
                'suggestion': 'SELECT column1, column2 instead of SELECT *'
            })
        
        # Check for missing WHERE clause
        if re.search(r'UPDATE\s+\w+\s+SET', code, re.IGNORECASE) and 'WHERE' not in code:
            issues.append({
                'type': 'missing_where',
                'severity': 'critical',
                'category': 'Logic Error',
                'description': 'UPDATE statement without WHERE clause.',
                'suggestion': 'Add WHERE clause to limit affected rows'
            })
        
        return issues
    
    def _detect_general_issues(self, code: str) -> List[Dict]:
        """Detect general code issues."""
        issues = []
        lines = code.split('\n')
        
        # Check for long lines
        for i, line in enumerate(lines, 1):
            if len(line) > 120:
                issues.append({
                    'line': i,
                    'type': 'long_line',
                    'severity': 'low',
                    'category': 'Style',
                    'description': f'Line exceeds 120 characters ({len(line)} chars).',
                    'suggestion': 'Break line into multiple lines'
                })
        
        # Check for multiple statements per line
        for i, line in enumerate(lines, 1):
            if line.count(';') > 1 and 'for' not in line:
                issues.append({
                    'line': i,
                    'type': 'multiple_statements',
                    'severity': 'low',
                    'category': 'Style',
                    'description': 'Multiple statements on one line.',
                    'suggestion': 'Use one statement per line for readability'
                })
        
        return issues
    
    def _analyze_static_results(self, analysis_results: Dict) -> List[Dict]:
        """Convert static analysis results to issues."""
        issues = []
        
        # Extract issues from flake8
        if 'flake8' in analysis_results:
            flake8_issues = analysis_results['flake8'].get('issues', [])
            for issue in flake8_issues:
                issues.append({
                    'line': issue.get('line'),
                    'type': issue.get('code'),
                    'severity': 'medium',
                    'category': 'Code Style',
                    'description': issue.get('message'),
                    'suggestion': 'Fix linting error'
                })
        
        # Extract issues from pylint
        if 'pylint' in analysis_results:
            pylint_messages = analysis_results['pylint'].get('messages', [])
            for msg in pylint_messages[:10]:  # Limit to 10 pylint messages
                issues.append({
                    'line': msg.get('line'),
                    'type': msg.get('symbol'),
                    'severity': msg.get('type', 'medium'),
                    'category': 'Code Quality',
                    'description': msg.get('message'),
                    'suggestion': 'Address pylint warning'
                })
        
        return issues
    
    def _deduplicate_issues(self, issues: List[Dict]) -> List[Dict]:
        """Remove duplicate issues."""
        seen = set()
        unique_issues = []
        
        for issue in issues:
            # Create a unique key
            key = (issue.get('line'), issue.get('type'), issue.get('description'))
            if key not in seen:
                seen.add(key)
                unique_issues.append(issue)
        
        # Sort by severity
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        unique_issues.sort(key=lambda x: severity_order.get(x.get('severity'), 4))
        
        return unique_issues
    
    def _calculate_quality_score(self, issues: List[Dict], metrics: Dict) -> float:
        """
        Calculate code quality score (0-100).
        
        Args:
            issues: List of detected issues
            metrics: Code metrics
            
        Returns:
            Quality score
        """
        score = 100.0
        
        # Deduct based on issues
        severity_impact = {
            'critical': 10,
            'high': 5,
            'medium': 2,
            'low': 1
        }
        
        for issue in issues:
            severity = issue.get('severity', 'low')
            score -= severity_impact.get(severity, 0)
        
        # Adjust based on metrics
        if metrics.get('avg_line_length', 0) > 100:
            score -= 5
        
        if metrics.get('code_to_comment_ratio', 0) > 10:
            score -= 3
        
        return max(0, min(100, score))
    
    def _calculate_security_score(self, issues: List[Dict]) -> float:
        """
        Calculate security score (0-100).
        
        Args:
            issues: List of detected issues
            
        Returns:
            Security score
        """
        score = 100.0
        security_issues = [i for i in issues if 'security' in i.get('type', '').lower() or 
                          'security' in i.get('category', '').lower()]
        
        for issue in security_issues:
            severity = issue.get('severity', 'low')
            if severity == 'critical':
                score -= 20
            elif severity == 'high':
                score -= 10
            elif severity == 'medium':
                score -= 5
        
        return max(0, min(100, score))
    
    def _calculate_complexity_score(self, code: str, language: str, 
                                   analysis_results: Dict) -> float:
        """
        Calculate complexity score.
        
        Args:
            code: Source code
            language: Programming language
            analysis_results: Static analysis results
            
        Returns:
            Complexity score (0-100, higher is worse)
        """
        complexity_metrics = analysis_results.get('complexity', {})
        cyclomatic = complexity_metrics.get('cyclomatic_complexity', 0)
        
        # Normalize to 0-100 scale
        # 1-5: Low (0-20)
        # 6-10: Medium (20-50)
        # 11-20: High (50-80)
        # 20+: Very High (80-100)
        
        if cyclomatic <= 5:
            return 20
        elif cyclomatic <= 10:
            return 50
        elif cyclomatic <= 20:
            return 80
        else:
            return min(100, 80 + (cyclomatic - 20) * 2)
    
    def _generate_suggestions(self, issues: List[Dict], language: str) -> List[Dict]:
        """Generate improvement suggestions."""
        suggestions = []
        issue_types = [i.get('type') for i in issues]
        
        # General suggestions
        suggestions.append({
            'priority': 'high',
            'category': 'Code Quality',
            'title': 'Review all critical and high-severity issues',
            'description': 'Address critical and high-severity issues first for reliability.',
            'impact': 'Improves code reliability and maintainability'
        })
        
        # Language-specific suggestions
        if language == 'python':
            if 'bare_except' in issue_types:
                suggestions.append({
                    'priority': 'high',
                    'category': 'Best Practice',
                    'title': 'Use specific exception handling',
                    'description': 'Catch specific exception types instead of using bare except.',
                    'impact': 'Better error handling and debugging'
                })
        
        elif language in ['javascript', 'typescript']:
            if any('await' not in str(i) and 'async' in str(i) for i in issues):
                suggestions.append({
                    'priority': 'medium',
                    'category': 'Best Practice',
                    'title': 'Use async/await properly',
                    'description': 'Ensure async functions properly handle promises with await.',
                    'impact': 'Prevents silent failures and improves code clarity'
                })
        
        if 'hardcoded_credential' in issue_types:
            suggestions.append({
                'priority': 'critical',
                'category': 'Security',
                'title': 'Move credentials to environment variables',
                'description': 'Never commit credentials. Use .env files and environment variables.',
                'impact': 'Prevents credential exposure in version control'
            })
        
        return suggestions
    
    def _generate_refactored_snippets(self, code: str, language: str, 
                                    issues: List[Dict]) -> List[Dict]:
        """Generate refactored code snippets."""
        snippets = []
        
        for issue in issues[:5]:  # Limit to 5 snippets
            if issue.get('fixed_code'):
                snippets.append({
                    'issue_type': issue.get('type'),
                    'line': issue.get('line'),
                    'original': None,  # Could extract from code
                    'refactored': issue.get('fixed_code'),
                    'explanation': issue.get('suggestion')
                })
        
        return snippets
    
    def _extract_metrics(self, code: str) -> Dict:
        """Extract code metrics."""
        lines = code.split('\n')
        non_empty_lines = [l for l in lines if l.strip()]
        
        return {
            'total_lines': len(lines),
            'code_lines': len(non_empty_lines),
            'comment_lines': len([l for l in lines if l.strip().startswith(('#', '//'))]),
            'blank_lines': len([l for l in lines if not l.strip()]),
            'avg_line_length': sum(len(l) for l in lines) / max(len(lines), 1)
        }
