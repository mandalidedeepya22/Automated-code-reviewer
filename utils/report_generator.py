"""
Report Generator module for creating PDF, HTML, and JSON reports.
Generates comprehensive code review reports with visualizations.
"""

import json
from datetime import datetime
from typing import Dict, Any, List
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generate comprehensive code review reports."""
    
    def __init__(self, report_dir: str = 'reports'):
        """
        Initialize report generator.
        
        Args:
            report_dir: Directory to save reports
        """
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(exist_ok=True)
        self.logger = logger
    
    def generate_json_report(self, review_data: Dict[str, Any], 
                            filename: str = None) -> str:
        """
        Generate JSON report.
        
        Args:
            review_data: Review results
            filename: Output filename
            
        Returns:
            Path to generated report
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f'review_{timestamp}.json'
            
            report_path = self.report_dir / filename
            
            with open(report_path, 'w') as f:
                json.dump(review_data, f, indent=2, default=str)
            
            self.logger.info(f"JSON report generated: {report_path}")
            return str(report_path)
        
        except Exception as e:
            self.logger.error(f"Error generating JSON report: {e}")
            return ""
    
    def generate_html_report(self, review_data: Dict[str, Any], 
                            filename: str = None) -> str:
        """
        Generate HTML report.
        
        Args:
            review_data: Review results
            filename: Output filename
            
        Returns:
            Path to generated report
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f'review_{timestamp}.html'
            
            report_path = self.report_dir / filename
            
            # Create HTML content
            html_content = self._build_html_report(review_data)
            
            with open(report_path, 'w') as f:
                f.write(html_content)
            
            self.logger.info(f"HTML report generated: {report_path}")
            return str(report_path)
        
        except Exception as e:
            self.logger.error(f"Error generating HTML report: {e}")
            return ""
    
    def _build_html_report(self, review_data: Dict[str, Any]) -> str:
        """Build HTML report content."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Extract data
        quality_score = review_data.get('quality_score', 0)
        security_score = review_data.get('security_score', 0)
        complexity_score = review_data.get('complexity_score', 0)
        issues = review_data.get('issues', [])
        suggestions = review_data.get('suggestions', [])
        refactored = review_data.get('refactored_snippets', [])
        language = review_data.get('language', 'Unknown')
        
        # Build issues HTML
        issues_html = ""
        if issues:
            issues_html = """
                <section class="section">
                    <h2>Issues Found</h2>
                    <div class="issues-container">
            """
            
            # Group by severity
            by_severity = {}
            for issue in issues:
                sev = issue.get('severity', 'low').upper()
                if sev not in by_severity:
                    by_severity[sev] = []
                by_severity[sev].append(issue)
            
            # Order by severity
            severity_order = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
            for severity in severity_order:
                if severity not in by_severity:
                    continue
                
                for issue in by_severity[severity]:
                    severity_color = {
                        'CRITICAL': '#d32f2f',
                        'HIGH': '#f57c00',
                        'MEDIUM': '#fbc02d',
                        'LOW': '#388e3c'
                    }.get(severity, '#757575')
                    
                    line_info = f"Line {issue.get('line')}" if issue.get('line') else "General"
                    
                    issues_html += f"""
                        <div class="issue-card" style="border-left: 4px solid {severity_color}">
                            <div class="issue-header">
                                <span class="severity" style="background-color: {severity_color}">
                                    {severity}
                                </span>
                                <span class="issue-type">{issue.get('type', 'Unknown')}</span>
                                <span class="issue-line">{line_info}</span>
                            </div>
                            <p class="issue-description">{issue.get('description', '')}</p>
                            <p class="issue-suggestion"><strong>Suggestion:</strong> {issue.get('suggestion', 'N/A')}</p>
                    """
                    
                    if issue.get('fixed_code'):
                        issues_html += f"""
                            <div class="code-block">
                                <pre><code>{self._escape_html(issue.get('fixed_code'))}</code></pre>
                            </div>
                        """
                    
                    issues_html += "</div>"
            
            issues_html += """
                    </div>
                </section>
            """
        
        # Build suggestions HTML
        suggestions_html = ""
        if suggestions:
            suggestions_html = """
                <section class="section">
                    <h2>Recommendations</h2>
                    <div class="suggestions-container">
            """
            
            for suggestion in suggestions:
                priority_color = {
                    'critical': '#d32f2f',
                    'high': '#f57c00',
                    'medium': '#fbc02d',
                    'low': '#388e3c'
                }.get(suggestion.get('priority', 'low'), '#757575')
                
                suggestions_html += f"""
                    <div class="suggestion-card">
                        <div class="suggestion-header">
                            <h3>{suggestion.get('title', 'Improvement')}</h3>
                            <span class="priority" style="background-color: {priority_color}">
                                {suggestion.get('priority', 'low').upper()}
                            </span>
                        </div>
                        <p>{suggestion.get('description', '')}</p>
                        <p class="impact"><strong>Impact:</strong> {suggestion.get('impact', '')}</p>
                    </div>
                """
            
            suggestions_html += """
                    </div>
                </section>
            """
        
        # Build HTML
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Code Review Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }}
        
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 32px;
            margin-bottom: 10px;
        }}
        
        .header p {{
            opacity: 0.9;
        }}
        
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f5f5f5;
        }}
        
        .score-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }}
        
        .score-card h3 {{
            font-size: 14px;
            color: #666;
            margin-bottom: 10px;
            text-transform: uppercase;
        }}
        
        .score-value {{
            font-size: 36px;
            font-weight: bold;
            color: #667eea;
        }}
        
        .score-bar {{
            background: #e0e0e0;
            height: 6px;
            border-radius: 3px;
            margin-top: 10px;
            overflow: hidden;
        }}
        
        .score-fill {{
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            transition: width 0.3s ease;
        }}
        
        .content {{
            padding: 30px;
        }}
        
        .section {{
            margin-bottom: 30px;
        }}
        
        .section h2 {{
            font-size: 24px;
            margin-bottom: 20px;
            color: #333;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        
        .meta-info {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
            padding: 15px;
            background: #f9f9f9;
            border-radius: 8px;
        }}
        
        .meta-item {{
            font-size: 14px;
        }}
        
        .meta-item strong {{
            color: #667eea;
        }}
        
        .issues-container {{
            display: flex;
            flex-direction: column;
            gap: 15px;
        }}
        
        .issue-card {{
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 15px;
            transition: box-shadow 0.3s ease;
        }}
        
        .issue-card:hover {{
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }}
        
        .issue-header {{
            display: flex;
            gap: 10px;
            margin-bottom: 10px;
            align-items: center;
        }}
        
        .severity {{
            color: white;
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
            text-transform: uppercase;
        }}
        
        .issue-type {{
            color: #667eea;
            font-weight: 600;
            font-size: 14px;
        }}
        
        .issue-line {{
            color: #999;
            font-size: 12px;
            margin-left: auto;
        }}
        
        .issue-description {{
            color: #555;
            margin-bottom: 8px;
            font-size: 14px;
        }}
        
        .issue-suggestion {{
            color: #666;
            font-size: 13px;
            margin-bottom: 10px;
        }}
        
        .code-block {{
            background: #f5f5f5;
            border-left: 3px solid #667eea;
            border-radius: 4px;
            margin-top: 10px;
            overflow-x: auto;
        }}
        
        .code-block pre {{
            padding: 12px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            color: #333;
        }}
        
        .suggestions-container {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 15px;
        }}
        
        .suggestion-card {{
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 15px;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .suggestion-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }}
        
        .suggestion-header {{
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 10px;
        }}
        
        .suggestion-header h3 {{
            font-size: 16px;
            color: #333;
            flex: 1;
        }}
        
        .priority {{
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: bold;
            text-transform: uppercase;
            white-space: nowrap;
            margin-left: 10px;
        }}
        
        .suggestion-card p {{
            font-size: 13px;
            color: #666;
            line-height: 1.5;
            margin-bottom: 8px;
        }}
        
        .impact {{
            color: #667eea;
            font-weight: 600;
            font-size: 12px;
        }}
        
        .footer {{
            background: #f5f5f5;
            padding: 20px;
            text-align: center;
            color: #666;
            font-size: 12px;
            border-top: 1px solid #e0e0e0;
        }}
        
        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            
            .container {{
                box-shadow: none;
            }}
            
            .summary {{
                page-break-after: avoid;
            }}
        }}
        
        .no-issues {{
            color: #388e3c;
            font-size: 16px;
            padding: 20px;
            text-align: center;
            background: #f1f8e9;
            border-radius: 8px;
            border-left: 4px solid #388e3c;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Code Review Report</h1>
            <p>Generated on {timestamp}</p>
        </div>
        
        <div class="summary">
            <div class="score-card">
                <h3>Quality Score</h3>
                <div class="score-value">{quality_score:.0f}</div>
                <div class="score-bar">
                    <div class="score-fill" style="width: {quality_score}%"></div>
                </div>
            </div>
            
            <div class="score-card">
                <h3>Security Score</h3>
                <div class="score-value">{security_score:.0f}</div>
                <div class="score-bar">
                    <div class="score-fill" style="width: {security_score}%"></div>
                </div>
            </div>
            
            <div class="score-card">
                <h3>Complexity</h3>
                <div class="score-value">{100 - complexity_score:.0f}</div>
                <div class="score-bar">
                    <div class="score-fill" style="width: {100 - complexity_score}%"></div>
                </div>
            </div>
        </div>
        
        <div class="content">
            <section class="section">
                <h2>Summary</h2>
                <div class="meta-info">
                    <div class="meta-item"><strong>Language:</strong> {language}</div>
                    <div class="meta-item"><strong>Total Issues:</strong> {len(issues)}</div>
                    <div class="meta-item"><strong>Critical:</strong> {len([i for i in issues if i.get('severity') == 'critical'])}</div>
                    <div class="meta-item"><strong>High:</strong> {len([i for i in issues if i.get('severity') == 'high'])}</div>
                </div>
            </section>
            
            {issues_html if issues_html else '<div class="no-issues">✓ No significant issues found! Great job!</div>'}
            {suggestions_html}
        </div>
        
        <div class="footer">
            <p>This report was automatically generated by AI-Powered Code Reviewer</p>
        </div>
    </div>
</body>
</html>
        """
        
        return html
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters."""
        return (text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#39;'))
    
    def generate_markdown_report(self, review_data: Dict[str, Any], 
                                filename: str = None) -> str:
        """
        Generate Markdown report.
        
        Args:
            review_data: Review results
            filename: Output filename
            
        Returns:
            Path to generated report
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f'review_{timestamp}.md'
            
            report_path = self.report_dir / filename
            
            # Create Markdown content
            md_content = self._build_markdown_report(review_data)
            
            with open(report_path, 'w') as f:
                f.write(md_content)
            
            self.logger.info(f"Markdown report generated: {report_path}")
            return str(report_path)
        
        except Exception as e:
            self.logger.error(f"Error generating Markdown report: {e}")
            return ""
    
    def _build_markdown_report(self, review_data: Dict[str, Any]) -> str:
        """Build Markdown report content."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        md = f"""# Code Review Report

**Generated:** {timestamp}

## Summary

| Metric | Score |
|--------|-------|
| Code Quality | {review_data.get('quality_score', 0):.0f}/100 |
| Security | {review_data.get('security_score', 0):.0f}/100 |
| Complexity | {100 - review_data.get('complexity_score', 0):.0f}/100 |

**Language:** {review_data.get('language', 'Unknown')}

## Issues Found: {len(review_data.get('issues', []))}

"""
        
        # Group issues by severity
        issues_by_severity = {}
        for issue in review_data.get('issues', []):
            severity = issue.get('severity', 'low').upper()
            if severity not in issues_by_severity:
                issues_by_severity[severity] = []
            issues_by_severity[severity].append(issue)
        
        # Add issues
        severity_order = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
        for severity in severity_order:
            if severity not in issues_by_severity:
                continue
            
            md += f"\n### {severity} Issues\n\n"
            
            for i, issue in enumerate(issues_by_severity[severity], 1):
                line_info = f"(Line {issue.get('line')})" if issue.get('line') else ""
                md += f"**{i}. {issue.get('type', 'Unknown')}** {line_info}\n\n"
                md += f"- **Description:** {issue.get('description', 'N/A')}\n"
                md += f"- **Suggestion:** {issue.get('suggestion', 'N/A')}\n\n"
        
        # Add suggestions
        if review_data.get('suggestions'):
            md += "\n## Recommendations\n\n"
            for suggestion in review_data.get('suggestions', []):
                md += f"### {suggestion.get('title', 'Improvement')}\n\n"
                md += f"{suggestion.get('description', '')}\n\n"
                md += f"**Impact:** {suggestion.get('impact', '')}\n\n"
        
        return md
    
    def get_report_summary(self, review_data: Dict[str, Any]) -> Dict:
        """
        Get summary statistics from review data.
        
        Args:
            review_data: Review results
            
        Returns:
            Summary dictionary
        """
        issues = review_data.get('issues', [])
        
        return {
            'total_issues': len(issues),
            'critical': len([i for i in issues if i.get('severity') == 'critical']),
            'high': len([i for i in issues if i.get('severity') == 'high']),
            'medium': len([i for i in issues if i.get('severity') == 'medium']),
            'low': len([i for i in issues if i.get('severity') == 'low']),
            'quality_score': review_data.get('quality_score', 0),
            'security_score': review_data.get('security_score', 0),
            'complexity_score': review_data.get('complexity_score', 0),
            'language': review_data.get('language', 'Unknown'),
            'timestamp': datetime.now().isoformat()
        }
