"""
GitHub Integration module for connecting to repositories and pull requests.
Allows reviewing code from GitHub repositories.
"""

import os
import re
import requests
import json
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class GitHubFetcher:
    """Fetch and analyze code from GitHub repositories."""
    
    def __init__(self, github_token: Optional[str] = None):
        """
        Initialize GitHub fetcher.
        
        Args:
            github_token: GitHub personal access token
        """
        self.github_token = github_token or os.environ.get('GITHUB_TOKEN')
        self.api_base = 'https://api.github.com'
        self.headers = self._get_headers()
        self.logger = logger
    
    def _get_headers(self) -> Dict:
        """Get headers for GitHub API requests."""
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'CodeReviewer'
        }
        
        if self.github_token:
            headers['Authorization'] = f'token {self.github_token}'
        
        return headers
    
    def _parse_repo_url(self, repo_url: str) -> Optional[Tuple[str, str]]:
        """
        Parse a GitHub repository URL into owner and repo name.
        """
        if not repo_url:
            return None
        repo_url = repo_url.strip()
        repo_url = repo_url.rstrip('/')
        match = re.search(
            r'github\.com[:/](?P<owner>[\w.-]+)/(?P<repo>[\w.-]+?)(?=\.git$|$)',
            repo_url
        )
        if match:
            return match.group('owner'), match.group('repo')
        return None
    
    def validate_connection(self) -> Tuple[bool, str]:
        """
        Validate GitHub connection.
        
        Returns:
            Tuple of (is_valid, message)
        """
        try:
            response = requests.get(
                f'{self.api_base}/user',
                headers=self.headers,
                timeout=5
            )
            
            if response.status_code == 200:
                user_data = response.json()
                return True, f"Connected as {user_data.get('login', 'Unknown')}"
            elif response.status_code == 401:
                return False, "Invalid GitHub token"
            else:
                return False, f"Connection failed: {response.status_code}"
        
        except Exception as e:
            return False, f"Connection error: {str(e)}"
    
    def fetch_repository(self, repo_url: str) -> Optional[Dict]:
        """
        Fetch repository information.
        
        Args:
            repo_url: GitHub repository URL (https://github.com/owner/repo)
            
        Returns:
            Repository info or None
        """
        try:
            # Parse repository URL
            parts = repo_url.strip('/').split('/')
            if len(parts) < 2:
                return None
            
            owner = parts[-2]
            repo = parts[-1].replace('.git', '')
            
            response = requests.get(
                f'{self.api_base}/repos/{owner}/{repo}',
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                repo_data = response.json()
                self.logger.info(f"Repository fetched: {owner}/{repo}")
                return {
                    'name': repo_data.get('name'),
                    'owner': owner,
                    'url': repo_data.get('html_url'),
                    'description': repo_data.get('description'),
                    'language': repo_data.get('language'),
                    'stars': repo_data.get('stargazers_count'),
                    'forks': repo_data.get('forks_count'),
                    'clone_url': repo_data.get('clone_url')
                }
            else:
                self.logger.error(f"Failed to fetch repository: {response.status_code}")
                return None
        
        except Exception as e:
            self.logger.error(f"Error fetching repository: {e}")
            return None
    
    def get_repository_files(self, owner: str, repo: str, 
                            path: str = '', branch: str = 'main') -> List[Dict]:
        """
        Get list of files in repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            path: Path within repository
            branch: Branch name
            
        Returns:
            List of file information
        """
        try:
            response = requests.get(
                f'{self.api_base}/repos/{owner}/{repo}/contents/{path}?ref={branch}',
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                files = response.json()
                if isinstance(files, list):
                    repository_files = []
                    for item in files:
                        if item.get('type') == 'dir':
                            repository_files.extend(self.get_repository_files(
                                owner, repo, item.get('path', ''), branch
                            ))
                        else:
                            repository_files.append(item)
                    return repository_files
            
            return []
        
        except Exception as e:
            self.logger.error(f"Error getting repository files: {e}")
            return []
    
    def get_file_content(self, owner: str, repo: str, 
                        file_path: str, branch: str = 'main') -> Optional[str]:
        """
        Get content of a specific file.
        
        Args:
            owner: Repository owner
            repo: Repository name
            file_path: Path to file
            branch: Branch name
            
        Returns:
            File content or None
        """
        try:
            response = requests.get(
                f'{self.api_base}/repos/{owner}/{repo}/contents/{file_path}?ref={branch}',
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                file_data = response.json()
                
                # Decode content if base64 encoded
                if 'content' in file_data:
                    import base64
                    content = base64.b64decode(file_data['content']).decode('utf-8')
                    return content
            
            return None
        
        except Exception as e:
            self.logger.error(f"Error getting file content: {e}")
            return None
    
    def list_pull_requests(self, owner: str, repo: str, 
                          state: str = 'open', limit: int = 10) -> List[Dict]:
        """
        List pull requests.
        
        Args:
            owner: Repository owner
            repo: Repository name
            state: PR state (open, closed, all)
            limit: Maximum number of PRs
            
        Returns:
            List of PR information
        """
        try:
            response = requests.get(
                f'{self.api_base}/repos/{owner}/{repo}/pulls?state={state}&per_page={limit}',
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                prs = response.json()
                return [
                    {
                        'id': pr.get('id'),
                        'number': pr.get('number'),
                        'title': pr.get('title'),
                        'state': pr.get('state'),
                        'author': pr.get('user', {}).get('login'),
                        'created_at': pr.get('created_at'),
                        'updated_at': pr.get('updated_at'),
                        'html_url': pr.get('html_url'),
                        'branch': pr.get('head', {}).get('ref')
                    }
                    for pr in prs
                ]
            
            return []
        
        except Exception as e:
            self.logger.error(f"Error listing pull requests: {e}")
            return []
    
    def get_pull_request_files(self, owner: str, repo: str, 
                              pr_number: int) -> List[Dict]:
        """
        Get files changed in a pull request.
        
        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number
            
        Returns:
            List of changed files
        """
        try:
            response = requests.get(
                f'{self.api_base}/repos/{owner}/{repo}/pulls/{pr_number}/files',
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                files = response.json()
                return [
                    {
                        'filename': f.get('filename'),
                        'status': f.get('status'),
                        'additions': f.get('additions'),
                        'deletions': f.get('deletions'),
                        'changes': f.get('changes'),
                        'patch': f.get('patch'),
                        'contents_url': f.get('contents_url')
                    }
                    for f in files
                ]
            
            return []
        
        except Exception as e:
            self.logger.error(f"Error getting PR files: {e}")
            return []
    
    def get_pull_request_diff(self, owner: str, repo: str, 
                             pr_number: int) -> Optional[str]:
        """
        Get complete diff for a pull request.
        
        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number
            
        Returns:
            Diff content or None
        """
        try:
            response = requests.get(
                f'{self.api_base}/repos/{owner}/{repo}/pulls/{pr_number}',
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                # Get diff from another endpoint
                diff_response = requests.get(
                    f'{self.api_base}/repos/{owner}/{repo}/pulls/{pr_number}',
                    headers={**self.headers, 'Accept': 'application/vnd.github.v3.diff'},
                    timeout=10
                )
                
                if diff_response.status_code == 200:
                    return diff_response.text
            
            return None
        
        except Exception as e:
            self.logger.error(f"Error getting PR diff: {e}")
            return None
    
    def get_commit_diff(self, owner: str, repo: str, 
                       commit_sha: str) -> Optional[str]:
        """
        Get diff for a specific commit.
        
        Args:
            owner: Repository owner
            repo: Repository name
            commit_sha: Commit SHA
            
        Returns:
            Diff content or None
        """
        try:
            diff_response = requests.get(
                f'{self.api_base}/repos/{owner}/{repo}/commits/{commit_sha}',
                headers={**self.headers, 'Accept': 'application/vnd.github.v3.diff'},
                timeout=10
            )
            
            if diff_response.status_code == 200:
                return diff_response.text
            
            return None
        
        except Exception as e:
            self.logger.error(f"Error getting commit diff: {e}")
            return None
    
    def create_pull_request_comment(self, owner: str, repo: str, 
                                   pr_number: int, body: str) -> bool:
        """
        Create a comment on a pull request.
        
        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number
            body: Comment body
            
        Returns:
            True if successful
        """
        try:
            response = requests.post(
                f'{self.api_base}/repos/{owner}/{repo}/issues/{pr_number}/comments',
                headers=self.headers,
                json={'body': body},
                timeout=10
            )
            
            if response.status_code == 201:
                self.logger.info(f"Comment created on PR #{pr_number}")
                return True
            else:
                self.logger.error(f"Failed to create comment: {response.status_code}")
                return False
        
        except Exception as e:
            self.logger.error(f"Error creating PR comment: {e}")
            return False
    
    def create_pull_request_review(self, owner: str, repo: str, 
                                  pr_number: int, body: str, 
                                  comments: List[Dict] = None) -> bool:
        """
        Create a review on a pull request.
        
        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number
            body: Review body
            comments: List of inline comment data
            
        Returns:
            True if successful
        """
        try:
            payload = {
                'body': body,
                'event': 'COMMENT'
            }
            
            if comments:
                payload['comments'] = comments
            
            response = requests.post(
                f'{self.api_base}/repos/{owner}/{repo}/pulls/{pr_number}/reviews',
                headers=self.headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                self.logger.info(f"Review created on PR #{pr_number}")
                return True
            else:
                self.logger.error(f"Failed to create review: {response.status_code}")
                return False
        
        except Exception as e:
            self.logger.error(f"Error creating PR review: {e}")
            return False
    
    def get_repository_languages(self, owner: str, repo: str) -> Dict[str, int]:
        """
        Get programming languages used in repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            Dictionary of language: bytes
        """
        try:
            response = requests.get(
                f'{self.api_base}/repos/{owner}/{repo}/languages',
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            
            return {}
        
        except Exception as e:
            self.logger.error(f"Error getting repository languages: {e}")
            return {}
    
    def get_rate_limit(self) -> Dict:
        """
        Get GitHub API rate limit information.
        
        Returns:
            Rate limit information
        """
        try:
            response = requests.get(
                f'{self.api_base}/rate_limit',
                headers=self.headers,
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            
            return {}
        
        except Exception as e:
            self.logger.error(f"Error getting rate limit: {e}")
            return {}
