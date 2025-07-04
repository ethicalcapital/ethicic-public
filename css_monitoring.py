#!/usr/bin/env python3
"""
CSS Monitoring and Maintenance Script
Continuous monitoring for CSS conflicts and regressions
"""

import os
import sys
import re
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple


class CSSMonitor:
    """Monitor CSS files for conflicts and regressions."""
    
    def __init__(self, css_dir: str = "static/css"):
        self.css_dir = Path(css_dir)
        self.theme_file = self.css_dir / 'garden-ui-theme.css'
        self.report_file = Path('css_monitoring_report.json')
        self.baseline_file = Path('css_baseline.json')
        
    def get_defined_variables(self) -> Set[str]:
        """Get all defined CSS variables from theme file."""
        defined_vars = set()
        
        if self.theme_file.exists():
            with open(self.theme_file, 'r') as f:
                content = f.read()
            defined_vars = set(re.findall(r'--[\w-]+', content))
        
        return defined_vars
    
    def scan_css_files(self) -> Dict:
        """Scan all CSS files for issues."""
        defined_vars = self.get_defined_variables()
        css_files = list(self.css_dir.glob('**/*.css'))
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'total_files': len(css_files),
            'total_defined_vars': len(defined_vars),
            'files_with_issues': [],
            'undefined_variables': {},
            'hardcoded_colors': {},
            'file_sizes': {},
            'total_undefined_vars': 0
        }
        
        for css_file in css_files:
            if css_file.name.startswith('.'):
                continue
            
            file_analysis = self._analyze_file(css_file, defined_vars)
            
            if file_analysis['issues']:
                results['files_with_issues'].append(css_file.name)
            
            if file_analysis['undefined_vars']:
                results['undefined_variables'][css_file.name] = file_analysis['undefined_vars']
                results['total_undefined_vars'] += len(file_analysis['undefined_vars'])
            
            if file_analysis['hardcoded_colors']:
                results['hardcoded_colors'][css_file.name] = file_analysis['hardcoded_colors']
            
            results['file_sizes'][css_file.name] = file_analysis['size_kb']
        
        return results
    
    def _analyze_file(self, css_file: Path, defined_vars: Set[str]) -> Dict:
        """Analyze a single CSS file for issues."""
        try:
            with open(css_file, 'r') as f:
                content = f.read()
        except Exception as e:
            return {
                'issues': True,
                'error': str(e),
                'undefined_vars': [],
                'hardcoded_colors': [],
                'size_kb': 0
            }
        
        # Find undefined variables
        used_vars = re.findall(r'var\((--[\w-]+)', content)
        undefined_vars = [var for var in used_vars if var not in defined_vars]
        
        # Find hardcoded colors (excluding comments and theme definitions)
        lines = content.split('\n')
        hardcoded_colors = []
        
        for i, line in enumerate(lines, 1):
            if '/*' in line or line.strip().startswith('*') or '--garden-accent:' in line:
                continue
            
            hex_colors = re.findall(r'(?<!-)#[0-9a-fA-F]{3,6}(?!\s*;?\s*\/\*)', line)
            if hex_colors:
                hardcoded_colors.extend([(i, color) for color in hex_colors])
        
        # File size
        size_kb = round(css_file.stat().st_size / 1024, 2)
        
        # Theme file is expected to have hardcoded colors
        is_theme_file = css_file.name == 'garden-ui-theme.css'
        hardcoded_issue = len(hardcoded_colors) > 5 and not is_theme_file
        
        return {
            'issues': bool(undefined_vars or hardcoded_issue),
            'undefined_vars': list(set(undefined_vars)),  # Remove duplicates
            'hardcoded_colors': hardcoded_colors[:5],  # Limit for report
            'size_kb': size_kb,
            'is_theme_file': is_theme_file
        }
    
    def create_baseline(self) -> None:
        """Create a baseline snapshot of current CSS state."""
        baseline = self.scan_css_files()
        baseline['is_baseline'] = True
        baseline['baseline_created'] = datetime.now().isoformat()
        
        with open(self.baseline_file, 'w') as f:
            json.dump(baseline, f, indent=2)
        
        print(f"✅ Baseline created: {baseline['total_undefined_vars']} undefined vars in {len(baseline['files_with_issues'])} files")
    
    def check_against_baseline(self) -> bool:
        """Check current state against baseline."""
        if not self.baseline_file.exists():
            print("❌ No baseline found. Run with --create-baseline first.")
            return False
        
        with open(self.baseline_file, 'r') as f:
            baseline = json.load(f)
        
        current = self.scan_css_files()
        
        # Compare key metrics
        regression_found = False
        
        if current['total_undefined_vars'] > baseline['total_undefined_vars']:
            print(f"❌ REGRESSION: Undefined variables increased from {baseline['total_undefined_vars']} to {current['total_undefined_vars']}")
            regression_found = True
        
        if len(current['files_with_issues']) > len(baseline['files_with_issues']):
            print(f"❌ REGRESSION: Files with issues increased from {len(baseline['files_with_issues'])} to {len(current['files_with_issues'])}")
            regression_found = True
        
        # Check for new problematic files
        new_problem_files = set(current['files_with_issues']) - set(baseline['files_with_issues'])
        if new_problem_files:
            print(f"❌ NEW PROBLEM FILES: {new_problem_files}")
            regression_found = True
        
        # Save current report
        with open(self.report_file, 'w') as f:
            json.dump(current, f, indent=2)
        
        if not regression_found:
            print(f"✅ No regressions detected!")
            print(f"   - Undefined variables: {current['total_undefined_vars']}")
            print(f"   - Files with issues: {len(current['files_with_issues'])}")
            print(f"   - Total CSS files: {current['total_files']}")
        
        return not regression_found
    
    def generate_report(self) -> str:
        """Generate a human-readable report."""
        current = self.scan_css_files()
        
        report = f"""
CSS MONITORING REPORT
Generated: {current['timestamp']}
{'='*50}

SUMMARY:
- Total CSS files: {current['total_files']}
- Defined CSS variables: {current['total_defined_vars']}
- Undefined variables: {current['total_undefined_vars']}
- Files with issues: {len(current['files_with_issues'])}

"""
        
        if current['undefined_variables']:
            report += "UNDEFINED VARIABLES:\n"
            for file_name, vars_list in current['undefined_variables'].items():
                report += f"  {file_name}: {vars_list[:3]}{'...' if len(vars_list) > 3 else ''}\n"
            report += "\n"
        
        if current['hardcoded_colors']:
            report += "HARDCODED COLORS:\n"
            for file_name, colors in current['hardcoded_colors'].items():
                if len(colors) > 5:  # Only report excessive hardcoding
                    report += f"  {file_name}: {len(colors)} hardcoded colors\n"
            report += "\n"
        
        # Large files
        large_files = {f: size for f, size in current['file_sizes'].items() if size > 100}
        if large_files:
            report += "LARGE CSS FILES (>100KB):\n"
            for file_name, size in sorted(large_files.items(), key=lambda x: x[1], reverse=True):
                report += f"  {file_name}: {size}KB\n"
            report += "\n"
        
        if current['total_undefined_vars'] == 0:
            report += "🎉 EXCELLENT: No undefined variables found!\n"
        elif current['total_undefined_vars'] < 10:
            report += "✅ GOOD: Very few undefined variables\n"
        else:
            report += "⚠️  NEEDS ATTENTION: Many undefined variables\n"
        
        return report
    
    def auto_fix_common_issues(self) -> List[str]:
        """Attempt to auto-fix common CSS issues."""
        fixes_applied = []
        
        # This would implement automatic fixes for common patterns
        # For now, just return suggestions
        current = self.scan_css_files()
        
        if current['total_undefined_vars'] > 0:
            fixes_applied.append(f"Found {current['total_undefined_vars']} undefined variables that need manual review")
        
        return fixes_applied


def main():
    """Main CLI interface."""
    import argparse
    
    parser = argparse.ArgumentParser(description='CSS Monitoring and Maintenance')
    parser.add_argument('--create-baseline', action='store_true', help='Create baseline snapshot')
    parser.add_argument('--check', action='store_true', help='Check against baseline')
    parser.add_argument('--report', action='store_true', help='Generate detailed report')
    parser.add_argument('--auto-fix', action='store_true', help='Attempt to auto-fix issues')
    parser.add_argument('--css-dir', default='static/css', help='CSS directory path')
    
    args = parser.parse_args()
    
    monitor = CSSMonitor(args.css_dir)
    
    if args.create_baseline:
        monitor.create_baseline()
    elif args.check:
        success = monitor.check_against_baseline()
        sys.exit(0 if success else 1)
    elif args.report:
        print(monitor.generate_report())
    elif args.auto_fix:
        fixes = monitor.auto_fix_common_issues()
        for fix in fixes:
            print(f"🔧 {fix}")
    else:
        # Default: quick check
        current = monitor.scan_css_files()
        print(f"CSS Status: {current['total_undefined_vars']} undefined vars, {len(current['files_with_issues'])} problematic files")
        
        if current['total_undefined_vars'] == 0:
            print("🎉 All CSS files are conflict-free!")
        else:
            print("⚠️  Issues detected. Run with --report for details.")


if __name__ == '__main__':
    main()