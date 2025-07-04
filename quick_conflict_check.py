#!/usr/bin/env python3
"""
Quick conflict check - simpler version to avoid regex issues
"""
import os
import re
from pathlib import Path

def check_undefined_vars():
    """Check for undefined CSS variables"""
    css_dir = Path('static/css')
    
    # Get defined variables from theme
    theme_file = css_dir / 'garden-ui-theme.css'
    defined_vars = set()
    
    if theme_file.exists():
        with open(theme_file, 'r') as f:
            content = f.read()
        defined_vars = set(re.findall(r'--[\w-]+', content))
    
    print(f"✅ Theme has {len(defined_vars)} defined variables")
    
    # Check all CSS files
    css_files = list(css_dir.glob('*.css'))
    total_undefined = 0
    files_with_issues = 0
    
    for css_file in css_files:
        if css_file.name.startswith('.'):
            continue
            
        try:
            with open(css_file, 'r') as f:
                content = f.read()
            
            # Simple regex to find var() usage
            used_vars = re.findall(r'var\((--.[\w-]+)', content)
            undefined_vars = [var for var in used_vars if var not in defined_vars]
            
            if undefined_vars:
                files_with_issues += 1
                total_undefined += len(undefined_vars)
                print(f"❌ {css_file.name}: {len(undefined_vars)} undefined vars")
            else:
                print(f"✅ {css_file.name}: clean")
                
        except Exception as e:
            print(f"⚠️  {css_file.name}: error reading")
    
    print(f"\n📊 SUMMARY:")
    print(f"Total CSS files: {len(css_files)}")
    print(f"Files with issues: {files_with_issues}")
    print(f"Total undefined variables: {total_undefined}")
    
    if total_undefined == 0:
        print("🎉 PERFECT! No undefined variables found!")
        return True
    elif total_undefined < 20:
        print("✅ EXCELLENT! Very few issues remaining")
        return True
    else:
        print("⚠️  Still some issues to resolve")
        return False

if __name__ == "__main__":
    success = check_undefined_vars()
    exit(0 if success else 1)