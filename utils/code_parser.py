"""
Code parser module for language detection and code extraction.
Detects programming language, extracts functions, classes, and handles multiple files.
"""

import re
from pathlib import Path
from typing import Tuple, List, Dict, Optional
import logging
import chardet
import zipfile
import os

logger = logging.getLogger(__name__)


class CodeParser:
    """Parse and analyze source code files."""
    
    # File extensions for supported languages
    LANGUAGE_EXTENSIONS = {
        'python': ['.py'],
        'javascript': ['.js', '.jsx', '.ts', '.tsx'],
        'java': ['.java'],
        'c': ['.c', '.h'],
        'cpp': ['.cpp', '.cc', '.cxx', '.h', '.hpp'],
        'sql': ['.sql'],
        'html': ['.html', '.htm'],
        'css': ['.css', '.scss', '.sass', '.less'],
        'go': ['.go'],
        'rust': ['.rs'],
        'php': ['.php'],
        'ruby': ['.rb'],
        'csharp': ['.cs']
    }
    
    # Language patterns for better detection
    LANGUAGE_PATTERNS = {
        'python': [r'^\s*import\s+', r'^\s*from\s+.*\s+import', r'def\s+\w+\s*\('],
        'javascript': [r'function\s+\w+\s*\(', r'const\s+\w+\s*=', r'let\s+\w+\s*=', r'=>'],
        'java': [r'public\s+class\s+', r'import\s+java\.', r'public\s+static\s+void'],
        'cpp': [r'#include\s*[<"]', r'std::', r'void\s+\w+\s*\('],
        'sql': [r'SELECT\s+', r'INSERT\s+INTO', r'UPDATE\s+', r'DELETE\s+FROM'],
        'html': [r'<!DOCTYPE', r'<html', r'<body', r'<head'],
        'css': [r'[a-zA-Z0-9\-_]+\s*\{[^}]*:', r'@media'],
        'go': [r'package\s+', r'func\s+\w+\s*\(', r'import\s*\(']
    }
    
    def __init__(self):
        """Initialize code parser."""
        self.logger = logger
    
    def detect_language(self, filename: str, content: Optional[str] = None) -> str:
        """
        Detect programming language from filename and/or content.
        
        Args:
            filename: Source code filename
            content: Optional source code content for pattern matching
            
        Returns:
            Detected language or 'unknown'
        """
        # Check by file extension first
        file_ext = Path(filename).suffix.lower()
        for lang, extensions in self.LANGUAGE_EXTENSIONS.items():
            if file_ext in extensions:
                return lang
        
        # Check content if provided
        if content:
            return self._detect_by_content(content)
        
        return 'unknown'
    
    def _detect_by_content(self, content: str) -> str:
        """
        Detect language by analyzing code content.
        
        Args:
            content: Source code content
            
        Returns:
            Detected language or 'unknown'
        """
        for lang, patterns in self.LANGUAGE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, content, re.MULTILINE):
                    return lang
        return 'unknown'
    
    def extract_functions(self, code: str, language: str) -> List[Dict]:
        """
        Extract function/method definitions from code.
        
        Args:
            code: Source code
            language: Programming language
            
        Returns:
            List of function/method information
        """
        functions = []
        
        if language == 'python':
            pattern = r'^\s*(?:async\s+)?def\s+(\w+)\s*\((.*?)\):'
            matches = re.finditer(pattern, code, re.MULTILINE)
            for match in matches:
                functions.append({
                    'name': match.group(1),
                    'params': match.group(2),
                    'line': code[:match.start()].count('\n') + 1,
                    'type': 'function'
                })
        
        elif language in ['javascript', 'typescript']:
            # Arrow functions
            pattern = r'(?:const|let|var)\s+(\w+)\s*=\s*\((.*?)\)\s*=>'
            matches = re.finditer(pattern, code, re.MULTILINE)
            for match in matches:
                functions.append({
                    'name': match.group(1),
                    'params': match.group(2),
                    'line': code[:match.start()].count('\n') + 1,
                    'type': 'arrow_function'
                })
            
            # Regular functions
            pattern = r'function\s+(\w+)\s*\((.*?)\)'
            matches = re.finditer(pattern, code, re.MULTILINE)
            for match in matches:
                functions.append({
                    'name': match.group(1),
                    'params': match.group(2),
                    'line': code[:match.start()].count('\n') + 1,
                    'type': 'function'
                })
        
        elif language == 'java':
            pattern = r'(?:public|private|protected)?\s*(?:static)?\s*\w+\s+(\w+)\s*\((.*?)\)'
            matches = re.finditer(pattern, code, re.MULTILINE)
            for match in matches:
                functions.append({
                    'name': match.group(1),
                    'params': match.group(2),
                    'line': code[:match.start()].count('\n') + 1,
                    'type': 'method'
                })
        
        elif language == 'cpp':
            pattern = r'(?:void|int|bool|string|double|float)\s+(\w+)\s*\((.*?)\)'
            matches = re.finditer(pattern, code, re.MULTILINE)
            for match in matches:
                functions.append({
                    'name': match.group(1),
                    'params': match.group(2),
                    'line': code[:match.start()].count('\n') + 1,
                    'type': 'function'
                })
        
        return functions
    
    def extract_classes(self, code: str, language: str) -> List[Dict]:
        """
        Extract class definitions from code.
        
        Args:
            code: Source code
            language: Programming language
            
        Returns:
            List of class information
        """
        classes = []
        
        if language == 'python':
            pattern = r'^\s*class\s+(\w+)\s*(?:\((.*?)\))?:'
            matches = re.finditer(pattern, code, re.MULTILINE)
            for match in matches:
                classes.append({
                    'name': match.group(1),
                    'inherits': match.group(2),
                    'line': code[:match.start()].count('\n') + 1
                })
        
        elif language in ['javascript', 'typescript']:
            pattern = r'(?:class|interface)\s+(\w+)\s*(?:extends\s+(\w+))?'
            matches = re.finditer(pattern, code, re.MULTILINE)
            for match in matches:
                classes.append({
                    'name': match.group(1),
                    'inherits': match.group(2),
                    'line': code[:match.start()].count('\n') + 1
                })
        
        elif language == 'java':
            pattern = r'(?:public|private)?\s*class\s+(\w+)\s*(?:extends\s+(\w+))?'
            matches = re.finditer(pattern, code, re.MULTILINE)
            for match in matches:
                classes.append({
                    'name': match.group(1),
                    'inherits': match.group(2),
                    'line': code[:match.start()].count('\n') + 1
                })
        
        return classes
    
    def get_code_metrics(self, code: str) -> Dict:
        """
        Calculate basic code metrics.
        
        Args:
            code: Source code
            
        Returns:
            Dictionary of code metrics
        """
        lines = code.split('\n')
        non_empty_lines = [l for l in lines if l.strip()]
        comment_lines = [l for l in lines if l.strip().startswith('#') or 
                        l.strip().startswith('//') or l.strip().startswith('/*')]
        
        return {
            'total_lines': len(lines),
            'non_empty_lines': len(non_empty_lines),
            'code_lines': len(non_empty_lines),
            'comment_lines': len(comment_lines),
            'code_to_comment_ratio': len(non_empty_lines) / max(len(comment_lines), 1),
            'avg_line_length': sum(len(l) for l in lines) / max(len(lines), 1),
            'max_line_length': max((len(l) for l in lines), default=0)
        }
    
    def clean_code(self, code: str) -> str:
        """
        Clean and normalize code.
        
        Args:
            code: Source code
            
        Returns:
            Cleaned code
        """
        # Remove leading/trailing whitespace from lines
        lines = [line.rstrip() for line in code.split('\n')]
        
        # Remove trailing empty lines but keep structure
        while lines and not lines[-1]:
            lines.pop()
        
        return '\n'.join(lines)
    
    def split_into_chunks(self, code: str, max_chars: int = 5000) -> List[str]:
        """
        Split code into chunks for processing.
        
        Args:
            code: Source code
            max_chars: Maximum characters per chunk
            
        Returns:
            List of code chunks
        """
        if len(code) <= max_chars:
            return [code]
        
        chunks = []
        lines = code.split('\n')
        current_chunk = []
        current_size = 0
        
        for line in lines:
            line_size = len(line) + 1  # +1 for newline
            
            if current_size + line_size > max_chars and current_chunk:
                chunks.append('\n'.join(current_chunk))
                current_chunk = [line]
                current_size = line_size
            else:
                current_chunk.append(line)
                current_size += line_size
        
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        
        return chunks
    
    def extract_from_zip(self, zip_path: str) -> Dict[str, str]:
        """
        Extract code files from ZIP archive.
        
        Args:
            zip_path: Path to ZIP file
            
        Returns:
            Dictionary of {filename: content}
        """
        code_files = {}
        ignored_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv'}
        supported_extensions = set()
        for exts in self.LANGUAGE_EXTENSIONS.values():
            supported_extensions.update(exts)
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                for file_info in zip_ref.infolist():
                    # Skip directories
                    if file_info.is_dir():
                        continue
                    
                    # Skip ignored directories
                    if any(ignored in file_info.filename for ignored in ignored_dirs):
                        continue
                    
                    # Check if it's a supported code file
                    if Path(file_info.filename).suffix.lower() in supported_extensions:
                        try:
                            content = zip_ref.read(file_info).decode('utf-8', errors='ignore')
                            code_files[file_info.filename] = content
                        except Exception as e:
                            self.logger.warning(f"Failed to read {file_info.filename}: {e}")
            
            self.logger.info(f"Extracted {len(code_files)} code files from ZIP")
            return code_files
        
        except Exception as e:
            self.logger.error(f"Error extracting ZIP file: {e}")
            return {}
    
    def validate_code(self, code: str, language: str) -> Tuple[bool, str]:
        """
        Validate code format.
        
        Args:
            code: Source code
            language: Programming language
            
        Returns:
            Tuple of (is_valid, message)
        """
        if not code or not code.strip():
            return False, "Code is empty"
        
        if len(code) > 1000000:  # 1MB limit
            return False, "Code file too large (>1MB)"
        
        if language == 'unknown':
            return False, "Unable to detect programming language"
        
        return True, "Code is valid"
