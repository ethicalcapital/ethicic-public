#!/usr/bin/env python
"""
Create PRI DDQ page from markdown content (simplified version)
"""
import os
import sys
import django
import re

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ethicic.settings')
django.setup()

from wagtail.models import Page
from public_site.models import PRIDDQPage, HomePage
from django.utils import timezone

def parse_ddq_content():
    """Parse the PRI DDQ markdown file into sections."""
    
    with open('/Users/srvo/ethicic-public/pri_ddq.md', 'r') as f:
        content = f.read()
    
    # Extract sections based on the DDQ structure
    sections = {
        'strategy_governance': '',
        'esg_integration': '',
        'stewardship': '',
        'transparency': '',
        'climate': '',
        'reporting_verification': '',
        'additional': ''
    }
    
    full_content = content
    
    # Extract Strategy & Governance section
    match = re.search(r'## (?:\*\*)?1\\.?\s*POLICY AND GOVERNANCE(?:\*\*)?\s*(.*?)(?=## (?:\*\*)?2\\.?\s*INVESTMENT)', full_content, re.DOTALL)
    if match:
        sections['strategy_governance'] = format_section_content(match.group(1))
    
    # Extract ESG Integration section  
    match = re.search(r'## (?:\*\*)?2\\.?\s*INVESTMENT PROCESS(?:\*\*)?\s*(.*?)(?=## (?:\*\*)?3\\.?\s*STEWARDSHIP)', full_content, re.DOTALL)
    if match:
        sections['esg_integration'] = format_section_content(match.group(1))
    
    # Extract Stewardship section
    match = re.search(r'## (?:\*\*)?3\\.?\s*STEWARDSHIP(?:\*\*)?\s*(.*?)(?=## (?:\*\*)?4\\.?\s*TRANSPARENCY|## (?:\*\*)?4\\.?\s*CLIENT)', full_content, re.DOTALL)
    if match:
        sections['stewardship'] = format_section_content(match.group(1))
    
    # Extract Transparency/Client Reporting section
    match = re.search(r'## (?:\*\*)?4\\.?\s*(?:TRANSPARENCY|CLIENT REPORTING)(?:\*\*)?\s*(.*?)(?=## (?:\*\*)?5\\.?\s*CLIMATE)', full_content, re.DOTALL)
    if match:
        sections['transparency'] = format_section_content(match.group(1))
    
    # Extract Climate section
    match = re.search(r'## (?:\*\*)?5\\.?\s*CLIMATE(?:\*\*)?\s*(.*?)(?=## (?:\*\*)?6\\.?\s*REPORTING)', full_content, re.DOTALL)
    if match:
        sections['climate'] = format_section_content(match.group(1))
    
    # Extract Reporting & Verification section
    match = re.search(r'## (?:\*\*)?6\\.?\s*REPORTING AND VERIFICATION(?:\*\*)?\s*(.*?)(?=## (?:\*\*)?7\\.?\s*INTERNAL|$)', full_content, re.DOTALL)
    if match:
        sections['reporting_verification'] = format_section_content(match.group(1))
    
    # Extract Internal ESG Management section
    match = re.search(r'## (?:\*\*)?7\\.?\s*INTERNAL ESG MANAGEMENT(?:\*\*)?\s*(.*?)$', full_content, re.DOTALL)
    if match:
        sections['additional'] = format_section_content(match.group(1))
    
    return sections

def format_section_content(content):
    """Format markdown content for RichTextField."""
    lines = content.strip().split('\n')
    formatted_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Convert markdown bold to HTML
        line = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', line)
        
        # Format questions (numbered items)
        if re.match(r'^\d+\.\d+', line):
            # Extract question number and text
            match = re.match(r'^(\d+\.\d+)\s+(.*)$', line)
            if match:
                num, text = match.groups()
                formatted_lines.append(f'<h3 class="ddq-question">{num} {text}</h3>')
        # Format instruction text (italic in markdown)
        elif line.startswith('*') and line.endswith('*') and len(line) > 2:
            formatted_lines.append(f'<p class="ddq-instruction"><em>{line[1:-1]}</em></p>')
        # Format bullet points
        elif line.startswith('* '):
            formatted_lines.append(f'<li>{line[2:]}</li>')
        elif line.startswith('- '):
            formatted_lines.append(f'<li>{line[2:]}</li>')
        # Format numbered sub-items (i), ii), etc.
        elif re.match(r'^i+\)', line):
            formatted_lines.append(f'<p class="ddq-subitem">{line}</p>')
        # Regular paragraphs
        else:
            # Don't wrap if it's already HTML
            if not line.startswith('<'):
                formatted_lines.append(f'<p>{line}</p>')
            else:
                formatted_lines.append(line)
    
    # Wrap consecutive <li> items in <ul>
    final_lines = []
    in_list = False
    
    for line in formatted_lines:
        if line.startswith('<li>'):
            if not in_list:
                final_lines.append('<ul>')
                in_list = True
            final_lines.append(line)
        else:
            if in_list:
                final_lines.append('</ul>')
                in_list = False
            final_lines.append(line)
    
    if in_list:
        final_lines.append('</ul>')
    
    return '\n'.join(final_lines)

def update_pri_ddq_page():
    """Update the existing PRI DDQ page."""
    print("Updating PRI DDQ page...")
    
    # Parse the DDQ content
    sections = parse_ddq_content()
    
    # Get the existing page
    pri_ddq_page = PRIDDQPage.objects.first()
    
    if not pri_ddq_page:
        print("ERROR: No PRI DDQ page found!")
        return
    
    print(f"Updating PRI DDQ page: {pri_ddq_page.title}")
    
    # Update content without triggering sync_to_support_articles
    PRIDDQPage.objects.filter(id=pri_ddq_page.id).update(
        strategy_governance_content=sections['strategy_governance'],
        esg_integration_content=sections['esg_integration'],
        stewardship_content=sections['stewardship'],
        transparency_content=sections['transparency'],
        climate_content=sections['climate'],
        reporting_verification_content=sections['reporting_verification'],
        additional_content=sections['additional']
    )
    
    # Refresh and publish
    pri_ddq_page.refresh_from_db()
    pri_ddq_page.save_revision().publish()
    
    print("PRI DDQ page updated successfully!")
    print(f"URL: {pri_ddq_page.url}")

if __name__ == "__main__":
    update_pri_ddq_page()