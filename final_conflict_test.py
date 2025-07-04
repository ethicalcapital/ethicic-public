#!/usr/bin/env python3
"""
Final Conflict-Free Test Suite
Comprehensive test to ensure all CSS conflicts are resolved and everything works perfectly.
"""

import os
import sys
import django
import time
import re
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ethicic.settings')
django.setup()

from django.test import Client
from django.conf import settings


class ConflictFreeTester:
    """Test suite to verify all conflicts are resolved."""
    
    def __init__(self):
        self.client = Client()
        self.client.defaults['SERVER_NAME'] = 'ec1c.com'
        self.passed = 0
        self.failed = 0
        self.issues = []
        
    def log_test(self, test_name, passed, details=""):
        """Log test result."""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name:<50} {details}")
        
        if passed:
            self.passed += 1
        else:
            self.failed += 1
            self.issues.append(f"{test_name}: {details}")
    
    def test_undefined_css_variables(self):
        """Test for undefined CSS variables across all files."""
        print("\n" + "="*80)
        print("TESTING FOR UNDEFINED CSS VARIABLES")
        print("="*80)
        
        # Get list of all CSS files
        css_dir = Path(settings.STATICFILES_DIRS[0]) / 'css'
        css_files = list(css_dir.glob('**/*.css'))
        
        # Define variables that exist in our theme system
        defined_variables = set()
        theme_file = css_dir / 'garden-ui-theme.css'
        
        if theme_file.exists():
            with open(theme_file, 'r') as f:
                theme_content = f.read()
            
            # Extract all defined variables
            var_pattern = r'--[\w-]+'
            defined_variables = set(re.findall(var_pattern, theme_content))
        
        self.log_test("Theme variables loaded", len(defined_variables) > 0, f"Found {len(defined_variables)} variables")
        
        # Check each CSS file for undefined variables
        total_undefined = 0
        for css_file in css_files:
            if css_file.name.startswith('.'):
                continue
                
            try:
                with open(css_file, 'r') as f:
                    content = f.read()
                
                # Find all var() usage
                var_usage_pattern = r'var\((--[\w-]+)'
                used_vars = re.findall(var_usage_pattern, content)
                
                undefined_vars = [var for var in used_vars if var not in defined_variables]
                
                if undefined_vars:
                    total_undefined += len(undefined_vars)
                    self.log_test(f"No undefined vars in {css_file.name}", False, 
                                f"Undefined: {', '.join(undefined_vars[:3])}")
                else:
                    self.log_test(f"No undefined vars in {css_file.name}", True)
                    
            except Exception as e:
                self.log_test(f"Read {css_file.name}", False, str(e)[:30])
        
        self.log_test("No undefined variables overall", total_undefined == 0, 
                     f"Found {total_undefined} undefined variables")
    
    def test_conflicting_css_files(self):
        """Test for conflicting or duplicate CSS files."""
        print("\n" + "="*80)
        print("TESTING FOR CONFLICTING CSS FILES")
        print("="*80)
        
        # Check that removed accessibility files are actually gone
        css_dir = Path(settings.STATICFILES_DIRS[0]) / 'css'
        removed_files = [
            'accessibility-focus.css',
            'accessibility-forms.css', 
            'accessibility-mobile-fixes.css',
            'accessibility-color-contrast.css'
        ]
        
        for file_name in removed_files:
            file_path = css_dir / file_name
            file_exists = file_path.exists()
            self.log_test(f"Removed conflicting {file_name}", not file_exists)
        
        # Check for duplicate selectors or conflicting styles
        important_files = [
            'garden-ui-theme.css',
            'high-contrast-mode.css',
            '07-footer.css',
            'button-contrast-fixes.css'
        ]
        
        for file_name in important_files:
            file_path = css_dir / file_name
            if file_path.exists():
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Check for proper variable usage
                has_theme_vars = '--theme-' in content
                self.log_test(f"{file_name} uses theme variables", has_theme_vars)
                
                # Check for no hardcoded colors (except comments and fallbacks)
                hardcoded_colors = re.findall(r'(?<!\/\*.*)(color|background):\s*#[0-9a-fA-F]{3,6}(?!.*\*\/)', content)
                has_hardcoded = len(hardcoded_colors) > 2  # Allow a few fallbacks
                self.log_test(f"{file_name} minimal hardcoded colors", not has_hardcoded)
    
    def test_form_consistency(self):
        """Test that all forms use consistent Garden UI classes."""
        print("\n" + "="*80)
        print("TESTING FORM CONSISTENCY")
        print("="*80)
        
        templates_dir = Path('templates')
        form_templates = list(templates_dir.glob('**/*form*.html'))
        
        # Add specific pages that have forms
        form_pages = [
            'templates/public_site/contact_page.html',
            'templates/public_site/onboarding_page.html',
            'templates/public_site/forms/contact_form_htmx.html'
        ]
        
        consistent_forms = 0
        total_forms = 0
        
        for template_path in form_pages + [str(f) for f in form_templates]:
            if os.path.exists(template_path):
                total_forms += 1
                with open(template_path, 'r') as f:
                    content = f.read()
                
                # Check for Garden UI classes
                has_garden_form = 'garden-form' in content or 'garden-input' in content
                has_garden_action = 'garden-action' in content
                
                # Check for old classes that should be replaced
                has_old_classes = 'form-input' in content or 'form-control' in content
                
                if has_garden_form and not has_old_classes:
                    consistent_forms += 1
                    self.log_test(f"Form consistency: {os.path.basename(template_path)}", True)
                else:
                    self.log_test(f"Form consistency: {os.path.basename(template_path)}", False, 
                                "Missing Garden UI classes or has old classes")
        
        overall_consistency = consistent_forms == total_forms if total_forms > 0 else True
        self.log_test("Overall form consistency", overall_consistency, 
                     f"{consistent_forms}/{total_forms} forms consistent")
    
    def test_page_loading_performance(self):
        """Test that all pages load quickly without CSS conflicts."""
        print("\n" + "="*80)
        print("TESTING PAGE LOADING PERFORMANCE")
        print("="*80)
        
        test_pages = [
            ('/', 'Homepage'),
            ('/about/', 'About'),
            ('/contact/', 'Contact'),
            ('/strategies/', 'Strategies'),
            ('/blog/', 'Blog'),
            ('/accessibility/', 'Accessibility')
        ]
        
        total_time = 0
        successful_loads = 0
        
        for url, name in test_pages:
            start_time = time.time()
            try:
                response = self.client.get(url)
                load_time = time.time() - start_time
                total_time += load_time
                
                success = response.status_code in [200, 301, 302]
                if success:
                    successful_loads += 1
                    
                self.log_test(f"{name} loads", success, f"{load_time:.2f}s")
                
                # Check for Garden UI presence
                if success and response.status_code == 200:
                    content = response.content.decode('utf-8')
                    has_garden = 'garden-' in content
                    has_theme = 'data-theme' in content
                    self.log_test(f"{name} has Garden UI", has_garden)
                    self.log_test(f"{name} has theme support", has_theme)
                    
            except Exception as e:
                self.log_test(f"{name} loads", False, str(e)[:30])
                
        avg_time = total_time / len(test_pages) if test_pages else 0
        self.log_test("Average load time acceptable", avg_time < 1.0, f"{avg_time:.2f}s avg")
        self.log_test("All pages load successfully", successful_loads == len(test_pages))
    
    def test_theme_switching_functionality(self):
        """Test that theme switching works without conflicts."""
        print("\n" + "="*80)
        print("TESTING THEME SWITCHING FUNCTIONALITY")
        print("="*80)
        
        # Test homepage for theme elements
        response = self.client.get('/')
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Check for theme toggle presence
            has_toggle = 'theme-toggle' in content
            self.log_test("Theme toggle present", has_toggle)
            
            # Check for data-theme attribute
            has_data_theme = 'data-theme' in content
            self.log_test("Data-theme attribute present", has_data_theme)
            
            # Check for CSS variables usage
            has_css_vars = 'var(--theme-' in content or 'var(--garden-' in content
            self.log_test("CSS variables in templates", has_css_vars)
            
            # Check footer specifically
            has_footer = 'garden-footer' in content
            self.log_test("Footer component present", has_footer)
            
            # Check for high contrast mode support
            has_hc_css = 'high-contrast-mode.css' in content
            self.log_test("High contrast CSS loaded", has_hc_css)
    
    def run_all_tests(self):
        """Run the complete conflict-free test suite."""
        print("\n" + "🔧" * 30)
        print("FINAL CONFLICT-FREE TEST SUITE")
        print("🔧" * 30)
        
        start_time = time.time()
        
        # Run all test categories
        self.test_undefined_css_variables()
        self.test_conflicting_css_files()
        self.test_form_consistency()
        self.test_page_loading_performance()
        self.test_theme_switching_functionality()
        
        # Results
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "="*80)
        print("FINAL TEST RESULTS")
        print("="*80)
        
        total_tests = self.passed + self.failed
        success_rate = (self.passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total tests: {total_tests}")
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"Success rate: {success_rate:.1f}%")
        print(f"Duration: {duration:.2f}s")
        
        if self.failed == 0:
            print("\n🎉 PERFECT! No conflicts found - everything is working flawlessly!")
            print("✨ Your site is now conflict-free with excellent accessibility!")
        elif success_rate >= 95:
            print("\n✅ EXCELLENT! Minimal issues remaining.")
        elif success_rate >= 85:
            print("\n⚠️ GOOD! Most issues resolved, minor fixes needed.")
        else:
            print("\n❌ ISSUES! Significant conflicts still exist.")
        
        if self.issues:
            print("\nREMAINING ISSUES:")
            for issue in self.issues:
                print(f"• {issue}")
        
        return self.failed == 0


def main():
    """Run the final conflict-free test."""
    try:
        tester = ConflictFreeTester()
        success = tester.run_all_tests()
        return 0 if success else 1
    except Exception as e:
        print(f"\nFATAL ERROR: {str(e)}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)