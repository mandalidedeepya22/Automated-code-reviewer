"""
Security Checker module for detecting security vulnerabilities.
Identifies SQL injection, hardcoded credentials, unsafe APIs, and more.
"""

import re
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class SecurityChecker:
    """Comprehensive security vulnerability checker."""
    
    # Dangerous patterns
    DANGEROUS_PATTERNS = {
        'sql_injection': [
            r"(?:SELECT|INSERT|UPDATE|DELETE).*?['\"].*?\+",
            r"(?:SELECT|INSERT|UPDATE|DELETE).*?['\"].*?%s",
            r"(?:SELECT|INSERT|UPDATE|DELETE).*?\.format\(",
        ],
        'command_injection': [
            r'os\.system\s*\(',
            r'subprocess\.call\s*\(',
            r'subprocess\.Popen\s*\(',
            r'exec\s*\(',
            r'eval\s*\(',
            r'system\s*\(',
            r'shell\s*=\s*True',
        ],
        'xss': [
            r'innerHTML\s*=',
            r'document\.write\(',
            r'\.html\(',
            r'dangerouslySetInnerHTML',
        ],
        'insecure_deserialization': [
            r'pickle\.load\s*\(',
            r'pickle\.loads\s*\(',
            r'yaml\.load\s*\(',
            r'json\.load\s*\(',  # If not using object_hook
        ],
        'weak_cryptography': [
            r'md5\(',
            r'sha1\(',
            r'hashlib\.md5\s*\(',
            r'hashlib\.sha1\s*\(',
            r'DES\(',
            r'RC4\(',
        ]
    }
    
    # Hardcoded secret patterns
    SECRET_PATTERNS = {
        'api_key': r'(?:api[_-]?key|apikey)\s*(?:=|:)\s*["\']([^"\']+)["\']',
        'password': r'(?:password|passwd|pwd)\s*(?:=|:)\s*["\']([^"\']+)["\']',
        'token': r'(?:token|auth_token|access_token)\s*(?:=|:)\s*["\']([^"\']+)["\']',
        'secret': r'(?:secret|client_secret)\s*(?:=|:)\s*["\']([^"\']+)["\']',
        'private_key': r'(?:private[_-]?key|privatekey)\s*(?:=|:)\s*["\']BEGIN[^"\']+["\']',
        'aws_key': r'(?:AKIA[0-9A-Z]{16})',
        'github_token': r'(?:ghp_[A-Za-z0-9_]+)',
        'stripe_key': r'(?:sk_live_[0-9a-zA-Z]+)',
    }
    
    # Unsafe function patterns
    UNSAFE_FUNCTIONS = {
        'python': {
            'eval': {'severity': 'critical', 'message': 'eval() is dangerous. Never use with untrusted input.'},
            'exec': {'severity': 'critical', 'message': 'exec() is dangerous. Use safer alternatives.'},
            'pickle.load': {'severity': 'high', 'message': 'pickle.load() unsafe with untrusted data. Use JSON instead.'},
            '__import__': {'severity': 'high', 'message': '__import__() can be a security risk.'},
        },
        'javascript': {
            'eval': {'severity': 'critical', 'message': 'eval() is dangerous. Never use with untrusted input.'},
            'Function': {'severity': 'high', 'message': 'Function() constructor can be a security risk.'},
            'innerHTML': {'severity': 'high', 'message': 'innerHTML can lead to XSS. Use textContent instead.'},
            'dangerouslySetInnerHTML': {'severity': 'high', 'message': 'dangerouslySetInnerHTML can lead to XSS.'},
        },
        'java': {
            'Runtime.exec': {'severity': 'critical', 'message': 'Runtime.exec() can lead to command injection.'},
            'System.load': {'severity': 'high', 'message': 'System.load() can be exploited.'},
            'ProcessBuilder': {'severity': 'high', 'message': 'ProcessBuilder() can lead to command injection.'},
        },
        'php': {
            'eval': {'severity': 'critical', 'message': 'eval() is dangerous. Never use.'},
            'exec': {'severity': 'critical', 'message': 'exec() unsafe with user input.'},
            'shell_exec': {'severity': 'critical', 'message': 'shell_exec() can lead to command injection.'},
            'system': {'severity': 'critical', 'message': 'system() is dangerous.'},
        }
    }
    
    def __init__(self):
        """Initialize security checker."""
        self.logger = logger
    
    def check_security(self, code: str, language: str) -> Dict[str, Any]:
        """
        Perform comprehensive security check.
        
        Args:
            code: Source code
            language: Programming language
            
        Returns:
            Security check results
        """
        results = {
            'language': language,
            'vulnerabilities': [],
            'secrets_found': [],
            'unsafe_functions': [],
            'security_score': 100,
            'high_risk_issues': []
        }
        
        # Check for various vulnerabilities
        results['vulnerabilities'].extend(self._check_injection_vulnerabilities(code))
        results['vulnerabilities'].extend(self._check_xss_vulnerabilities(code))
        results['vulnerabilities'].extend(self._check_insecure_practices(code, language))
        
        # Check for hardcoded secrets
        results['secrets_found'] = self._check_hardcoded_secrets(code)
        
        # Check for unsafe functions
        results['unsafe_functions'] = self._check_unsafe_functions(code, language)
        
        # Identify high-risk issues
        results['high_risk_issues'] = [v for v in results['vulnerabilities'] 
                                      if v.get('severity') in ['critical', 'high']]
        
        # Calculate security score
        results['security_score'] = self._calculate_security_score(results)
        
        return results
    
    def _check_injection_vulnerabilities(self, code: str) -> List[Dict]:
        """Check for SQL injection and command injection."""
        vulnerabilities = []
        
        # SQL Injection
        for pattern in self.DANGEROUS_PATTERNS['sql_injection']:
            matches = list(re.finditer(pattern, code, re.IGNORECASE))
            for match in matches:
                line_num = code[:match.start()].count('\n') + 1
                vulnerabilities.append({
                    'type': 'sql_injection',
                    'severity': 'critical',
                    'line': line_num,
                    'code': match.group(0),
                    'message': 'SQL injection risk: Never concatenate user input into SQL queries.',
                    'fix': 'Use parameterized queries or prepared statements.'
                })
        
        # Command Injection
        for pattern in self.DANGEROUS_PATTERNS['command_injection']:
            matches = list(re.finditer(pattern, code, re.IGNORECASE))
            for match in matches:
                line_num = code[:match.start()].count('\n') + 1
                vulnerabilities.append({
                    'type': 'command_injection',
                    'severity': 'critical',
                    'line': line_num,
                    'code': match.group(0),
                    'message': 'Command injection risk: Never pass user input to system commands.',
                    'fix': 'Use safer APIs or validate and sanitize input strictly.'
                })
        
        return vulnerabilities
    
    def _check_xss_vulnerabilities(self, code: str) -> List[Dict]:
        """Check for XSS vulnerabilities."""
        vulnerabilities = []
        
        for pattern in self.DANGEROUS_PATTERNS['xss']:
            matches = list(re.finditer(pattern, code))
            for match in matches:
                line_num = code[:match.start()].count('\n') + 1
                vulnerabilities.append({
                    'type': 'xss_vulnerability',
                    'severity': 'high',
                    'line': line_num,
                    'code': match.group(0),
                    'message': 'XSS risk: Never insert unsanitized user input into HTML.',
                    'fix': 'Use textContent instead of innerHTML, or sanitize HTML properly.'
                })
        
        return vulnerabilities
    
    def _check_insecure_practices(self, code: str, language: str) -> List[Dict]:
        """Check for insecure coding practices."""
        vulnerabilities = []
        
        # Weak cryptography
        for pattern in self.DANGEROUS_PATTERNS['weak_cryptography']:
            matches = list(re.finditer(pattern, code))
            for match in matches:
                line_num = code[:match.start()].count('\n') + 1
                vulnerabilities.append({
                    'type': 'weak_cryptography',
                    'severity': 'high',
                    'line': line_num,
                    'code': match.group(0),
                    'message': 'Weak cryptographic algorithm detected.',
                    'fix': 'Use SHA256, AES, or other strong algorithms.'
                })
        
        # Insecure deserialization
        if language == 'python':
            for pattern in self.DANGEROUS_PATTERNS['insecure_deserialization']:
                matches = list(re.finditer(pattern, code))
                for match in matches:
                    if 'pickle' in match.group(0):
                        line_num = code[:match.start()].count('\n') + 1
                        vulnerabilities.append({
                            'type': 'insecure_deserialization',
                            'severity': 'critical',
                            'line': line_num,
                            'code': match.group(0),
                            'message': 'Unsafe deserialization: pickle.load() can execute arbitrary code.',
                            'fix': 'Use JSON for untrusted data. Use pickle only with trusted sources.'
                        })
        
        # Check for unvalidated redirects
        if 'redirect' in code.lower():
            if not re.search(r'(?:validate|sanitize|allow.*list)', code, re.IGNORECASE):
                vulnerabilities.append({
                    'type': 'unvalidated_redirect',
                    'severity': 'high',
                    'message': 'Unvalidated redirect found. Validate redirect destinations.',
                    'fix': 'Validate redirect URLs against a whitelist.'
                })
        
        # Check for hardcoded file paths
        if re.search(r'["\']/(home|root|etc|var|tmp)', code):
            vulnerabilities.append({
                'type': 'hardcoded_path',
                'severity': 'medium',
                'message': 'Hardcoded absolute file paths detected.',
                'fix': 'Use configuration files or environment variables for paths.'
            })
        
        return vulnerabilities
    
    def _check_hardcoded_secrets(self, code: str) -> List[Dict]:
        """Check for hardcoded secrets and credentials."""
        secrets = []
        
        for secret_type, pattern in self.SECRET_PATTERNS.items():
            matches = list(re.finditer(pattern, code, re.IGNORECASE))
            for match in matches:
                line_num = code[:match.start()].count('\n') + 1
                secrets.append({
                    'type': secret_type,
                    'severity': 'critical',
                    'line': line_num,
                    'match': match.group(0)[:50] + '...',  # Truncate for display
                    'message': f'Hardcoded {secret_type} found. Remove before committing.',
                    'fix': 'Move to environment variables or secrets manager.'
                })
        
        return secrets
    
    def _check_unsafe_functions(self, code: str, language: str) -> List[Dict]:
        """Check for usage of unsafe functions."""
        unsafe_funcs = []
        
        unsafe_dict = self.UNSAFE_FUNCTIONS.get(language, {})
        
        for unsafe_func, details in unsafe_dict.items():
            # Create regex pattern
            pattern = unsafe_func.replace('.', r'\.')
            pattern = r'\b' + pattern + r'\s*\('
            
            matches = list(re.finditer(pattern, code, re.IGNORECASE))
            for match in matches:
                line_num = code[:match.start()].count('\n') + 1
                unsafe_funcs.append({
                    'function': unsafe_func,
                    'severity': details['severity'],
                    'line': line_num,
                    'message': details['message']
                })
        
        return unsafe_funcs
    
    def _check_access_control(self, code: str, language: str) -> List[Dict]:
        """Check for access control issues."""
        issues = []
        
        # Check for missing authentication checks
        if 'def ' in code or 'function ' in code:
            if 'route' in code.lower() or '@app' in code:
                if not re.search(r'(?:login|auth|permission|token)', code, re.IGNORECASE):
                    issues.append({
                        'type': 'missing_authentication',
                        'severity': 'high',
                        'message': 'Route found without authentication check.',
                        'fix': 'Add authentication/authorization checks.'
                    })
        
        return issues
    
    def _check_input_validation(self, code: str) -> List[Dict]:
        """Check for input validation issues."""
        issues = []
        
        # Check for functions receiving input without validation
        input_keywords = ['request', 'input', 'gets', 'scanf', 'readline']
        
        for keyword in input_keywords:
            if keyword in code.lower():
                # Check if followed by validation
                lines = code.split('\n')
                for i, line in enumerate(lines):
                    if keyword in line.lower():
                        # Look ahead for validation
                        validation_found = False
                        for j in range(i, min(i + 5, len(lines))):
                            if re.search(r'(?:validate|sanitize|check|assert)', lines[j], re.IGNORECASE):
                                validation_found = True
                                break
                        
                        if not validation_found:
                            issues.append({
                                'type': 'missing_input_validation',
                                'severity': 'high',
                                'line': i + 1,
                                'message': f'Input received but not validated.',
                                'fix': 'Always validate and sanitize user input.'
                            })
                            break
        
        return issues
    
    def _calculate_security_score(self, results: Dict) -> float:
        """
        Calculate overall security score (0-100).
        
        Args:
            results: Security check results
            
        Returns:
            Security score
        """
        score = 100.0
        
        # Deduct for vulnerabilities
        for vuln in results['vulnerabilities']:
            severity = vuln.get('severity', 'low')
            if severity == 'critical':
                score -= 10
            elif severity == 'high':
                score -= 5
            elif severity == 'medium':
                score -= 2
        
        # Deduct for secrets
        score -= len(results['secrets_found']) * 15
        
        # Deduct for unsafe functions
        for unsafe in results['unsafe_functions']:
            severity = unsafe.get('severity', 'low')
            if severity == 'critical':
                score -= 10
            elif severity == 'high':
                score -= 5
        
        return max(0, min(100, score))
    
    def get_security_summary(self, results: Dict) -> Dict:
        """
        Get summary of security findings.
        
        Args:
            results: Security check results
            
        Returns:
            Summary dictionary
        """
        return {
            'score': results['security_score'],
            'critical_issues': len([v for v in results['high_risk_issues'] if v.get('severity') == 'critical']),
            'high_issues': len([v for v in results['high_risk_issues'] if v.get('severity') == 'high']),
            'secrets_found': len(results['secrets_found']),
            'unsafe_functions': len(results['unsafe_functions']),
            'total_vulnerabilities': len(results['vulnerabilities']),
            'status': 'CRITICAL' if results['security_score'] < 40 else 
                     'HIGH RISK' if results['security_score'] < 70 else 
                     'MEDIUM RISK' if results['security_score'] < 90 else 'GOOD'
        }
