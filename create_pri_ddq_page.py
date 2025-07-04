#!/usr/bin/env python
"""
Create PRI DDQ page from markdown content
"""
import os
import django
import re

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ethicic.settings')
django.setup()

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
    
    # Current section being processed
    current_section = None
    current_content = []
    
    lines = content.split('\n')
    
    for line in lines:
        # Check for main section headers
        if '## **1\\. POLICY AND GOVERNANCE**' in line or '## 1. POLICY AND GOVERNANCE' in line:
            current_section = 'strategy_governance'
            current_content = []
        elif '## **2\\. INVESTMENT PROCESS**' in line or '## 2. INVESTMENT PROCESS' in line:
            current_section = 'esg_integration'
            current_content = []
        elif '## **3\\. STEWARDSHIP**' in line or '## 3. STEWARDSHIP' in line:
            current_section = 'stewardship'
            current_content = []
        elif '## **4\\. TRANSPARENCY**' in line or '## 4. TRANSPARENCY' in line:
            current_section = 'transparency'
            current_content = []
        elif '## **5\\. CLIMATE**' in line or '## 5. CLIMATE' in line:
            current_section = 'climate'
            current_content = []
        elif '## **6\\. REPORTING AND VERIFICATION**' in line or '## 6. REPORTING AND VERIFICATION' in line:
            current_section = 'reporting_verification'
            current_content = []
        elif '## **7\\. INTERNAL ESG MANAGEMENT**' in line or '## 7. INTERNAL ESG MANAGEMENT' in line:
            current_section = 'additional'
            current_content = []
        elif current_section:
            # Convert markdown to HTML-like format for RichTextField
            html_line = line
            
            # Convert bold markdown to HTML
            html_line = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html_line)
            
            # Convert numbered questions to headings
            if re.match(r'^\d+\.\d+\s+', html_line):
                html_line = re.sub(r'^(\d+\.\d+)\s+(.*)$', r'<h3>\1 \2</h3>', html_line)
            elif re.match(r'^\d+\.\s+\*\*', html_line):
                html_line = re.sub(r'^\d+\.\s+\*\*(.*?)\*\*', r'<h3>\1</h3>', html_line)
            
            # Convert italic text
            if html_line.startswith('*') and html_line.endswith('*') and not html_line.startswith('**'):
                html_line = f'<p class="ddq-instruction">{html_line[1:-1]}</p>'
            
            # Convert regular paragraphs
            if html_line and not html_line.startswith('<'):
                html_line = f'<p>{html_line}</p>'
            
            current_content.append(html_line)
    
    # Join content for each section
    for section in sections:
        if section in locals() and current_section == section:
            sections[section] = '\n'.join(current_content)
    
    # Parse the full content again to get all sections properly
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

def create_pri_ddq_page():
    """Create or update the PRI DDQ page."""
    print("Creating PRI DDQ page...")
    
    # Parse the DDQ content
    sections = parse_ddq_content()
    
    # Get the home page as parent
    home_page = HomePage.objects.first()
    if not home_page:
        print("ERROR: No home page found!")
        return
    
    # Check if PRI DDQ page already exists
    existing_page = PRIDDQPage.objects.first()
    
    if existing_page:
        print(f"Updating existing PRI DDQ page: {existing_page.title}")
        
        # Update content
        existing_page.strategy_governance_content = sections['strategy_governance']
        existing_page.esg_integration_content = sections['esg_integration']
        existing_page.stewardship_content = sections['stewardship']
        existing_page.transparency_content = sections['transparency']
        existing_page.climate_content = sections['climate']
        existing_page.reporting_verification_content = sections['reporting_verification']
        existing_page.additional_content = sections['additional']
        
        existing_page.save_revision().publish()
        print("PRI DDQ page updated successfully!")
    else:
        print("Creating new PRI DDQ page...")
        
        # Create new page
        pri_ddq_page = PRIDDQPage(
            title="PRI Due Diligence Questionnaire",
            slug="pri-ddq",
            hero_title="PRI Due Diligence Questionnaire",
            hero_subtitle="Comprehensive responses to Principles for Responsible Investment due diligence questions.",
            hero_description="<p>As a signatory-aligned investment manager, we provide detailed responses to standard PRI due diligence questions covering our ESG integration, stewardship practices, and responsible investment approach.</p>",
            executive_summary="<p>Ethical Capital Investment Management is a registered investment adviser specializing in values-based equity investing. We integrate comprehensive ESG criteria throughout our investment process, excluding 57% of the S&P 500 through our proprietary screening methodology.</p>",
            strategy_governance_content=sections['strategy_governance'],
            esg_integration_content=sections['esg_integration'],
            stewardship_content=sections['stewardship'],
            transparency_content=sections['transparency'],
            climate_content=sections['climate'],
            reporting_verification_content=sections['reporting_verification'],
            additional_content=sections['additional'],
            live=True,
            first_published_at=timezone.now()
        )
        
        # Add as child of home page
        home_page.add_child(instance=pri_ddq_page)
        pri_ddq_page.save_revision().publish()
        
        print("PRI DDQ page created successfully!")
        print("URL: /pri-ddq/")

if __name__ == "__main__":
    create_pri_ddq_page()