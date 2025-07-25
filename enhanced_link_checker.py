#!/usr/bin/env python3
"""
Enhanced Comprehensive Link Checker for ethicic.com
====================================================

This enhanced version provides more thorough link extraction from:
- Navigation menus (all levels)
- Page body content (all text and HTML)
- Footer links
- Blog post content
- Image src attributes
- CSS background-image references
- Inline styles and data attributes
- JavaScript-generated links
- Meta tags and structured data

Focus: More comprehensive content parsing and better categorization
"""

import asyncio
import json
import logging
import re
import ssl
import time
from collections import defaultdict
from datetime import datetime
from typing import Optional
from urllib.parse import unquote, urljoin, urlparse

import aiohttp
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class EnhancedLinkChecker:
    def __init__(self, base_url: str, max_concurrent: int = 10):
        self.base_url = base_url.rstrip("/")
        self.domain = urlparse(base_url).netloc
        self.max_concurrent = max_concurrent
        self.session = None

        # Comprehensive link storage
        self.all_links = set()
        self.pages_crawled = set()
        self.link_sources = defaultdict(list)  # Track where each link was found
        self.link_contexts = {}  # Store link text and surrounding context
        self.link_types = {}  # Categorize link types

        # Results storage
        self.results = {"working": [], "broken": [], "redirects": [], "errors": []}

        # Enhanced extraction patterns
        self.css_url_pattern = re.compile(
            r'url\s*\(\s*["\']?([^"\')]+)["\']?\s*\)', re.IGNORECASE
        )
        self.email_pattern = re.compile(r'mailto:([^\s<>"]+@[^\s<>"]+)', re.IGNORECASE)
        self.phone_pattern = re.compile(r"tel:([+\d\-\(\)\s]+)", re.IGNORECASE)
        self.javascript_url_pattern = re.compile(
            r'(?:href|src)\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE
        )

        # Skip patterns for irrelevant links
        self.skip_patterns = [
            r"^javascript:",
            r"^#$",
            r"^#[^/]",  # Fragment-only links
            r"^\s*$",  # Empty links
        ]

    async def __aenter__(self):
        """Async context manager entry"""
        connector = aiohttp.TCPConnector(
            limit=self.max_concurrent,
            ssl=ssl.create_default_context(),
            ttl_dns_cache=300,
            use_dns_cache=True,
        )

        timeout = aiohttp.ClientTimeout(total=30, connect=10, sock_read=10)

        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                "User-Agent": "Mozilla/5.0 (compatible; EthicicLinkChecker/2.0; +https://ethicic.com/robots.txt)",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
            },
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    def is_valid_link(self, url: str) -> bool:
        """Enhanced link validation with better filtering"""
        if not url or not url.strip():
            return False

        url = url.strip()

        # Skip patterns
        for pattern in self.skip_patterns:
            if re.match(pattern, url):
                return False

        # Skip data URLs, blob URLs, etc.
        if url.startswith(("data:", "blob:", "about:")):
            return False

        # Skip obvious non-URLs (metadata strings, descriptions, etc.)
        non_url_patterns = [
            r"^width=device-width",  # CSS viewport meta content
            r"^Ethical Capital provides",  # Description text
            r"^SettingModuleProxy",  # Django template variables
            r"^[a-zA-Z0-9]{20,}$",  # Long random strings without URL structure
            r"^ethical investing,",  # Keywords/tags
            r"^[A-Z][a-z]+ [A-Z]",  # Title case text (likely titles)
            r"^\d+$",  # Pure numbers
            r"^website$",  # Single word metadata
        ]

        for pattern in non_url_patterns:
            if re.match(pattern, url, re.IGNORECASE):
                return False

        # Must have valid URL structure
        if not (
            url.startswith(("http://", "https://", "mailto:", "tel:", "ftp://"))
            or url.startswith("/")
        ):
            # If it doesn't start with a protocol or root path, check if it looks like a relative URL
            if not re.match(r"^[a-zA-Z0-9._-]+(/[a-zA-Z0-9._-]*)*/?$", url):
                return False

        return True

    def normalize_url(self, url: str, base_url: str) -> str:
        """Enhanced URL normalization"""
        if not url:
            return ""

        url = url.strip().strip("'\"")

        # Handle special cases
        if url.startswith("//"):
            url = "https:" + url
        elif url.startswith("/") or not url.startswith(
            ("http://", "https://", "mailto:", "tel:", "ftp://")
        ):
            url = urljoin(base_url, url)

        # Clean up the URL
        url = unquote(url)
        url = re.sub(r"#.*$", "", url)  # Remove fragments for checking

        return url

    def extract_links_from_css(self, css_content: str, base_url: str) -> set[str]:
        """Extract URLs from CSS content"""
        links = set()

        # Find all url() references
        for match in self.css_url_pattern.finditer(css_content):
            url = match.group(1).strip("'\"")
            if self.is_valid_link(url):
                normalized = self.normalize_url(url, base_url)
                if normalized:
                    links.add(normalized)
                    self.link_types[normalized] = "css_asset"

        return links

    def extract_links_from_javascript(self, js_content: str, base_url: str) -> set[str]:
        """Extract URLs from JavaScript content"""
        links = set()

        # Look for URL patterns in JavaScript
        for match in self.javascript_url_pattern.finditer(js_content):
            url = match.group(1)
            if self.is_valid_link(url):
                normalized = self.normalize_url(url, base_url)
                if normalized:
                    links.add(normalized)
                    self.link_types[normalized] = "javascript_reference"

        return links

    def extract_comprehensive_links(
        self, soup: BeautifulSoup, page_url: str
    ) -> set[str]:
        """Enhanced comprehensive link extraction"""
        links = set()

        # 1. Standard HTML links
        for tag_info in [
            ("a", "href"),
            ("link", "href"),
            ("img", "src"),
            ("script", "src"),
            ("iframe", "src"),
            ("embed", "src"),
            ("object", "data"),
            ("source", "src"),
            ("track", "src"),
            ("area", "href"),
            ("base", "href"),
            ("form", "action"),
        ]:
            tag_name, attr_name = tag_info
            for element in soup.find_all(tag_name, **{attr_name: True}):
                url = element.get(attr_name)
                if self.is_valid_link(url):
                    normalized = self.normalize_url(url, page_url)
                    if normalized:
                        links.add(normalized)

                        # Store context information
                        link_text = (
                            element.get_text(strip=True)
                            or element.get("alt", "")
                            or element.get("title", "")
                        )
                        self.link_contexts[normalized] = {
                            "text": link_text[:100],  # First 100 chars
                            "tag": tag_name,
                            "page": page_url,
                        }

                        # Categorize link type
                        if tag_name == "a":
                            self.link_types[normalized] = "text_link"
                        elif tag_name in ["img", "source"]:
                            self.link_types[normalized] = "image"
                        elif tag_name in ["script", "link"]:
                            self.link_types[normalized] = "asset"
                        else:
                            self.link_types[normalized] = f"{tag_name}_reference"

        # 2. Meta tags and structured data (be more selective)
        for meta in soup.find_all("meta"):
            # Only extract from specific meta attributes that typically contain URLs
            if meta.get("property") in [
                "og:url",
                "og:image",
                "twitter:image",
            ] or meta.get("name") in ["twitter:image"]:
                url = meta.get("content")
                if url and self.is_valid_link(url):
                    normalized = self.normalize_url(url, page_url)
                    if normalized:
                        links.add(normalized)
                        self.link_types[normalized] = "meta_reference"

        # 3. CSS inline styles and stylesheets
        # Inline styles
        for element in soup.find_all(style=True):
            css_content = element.get("style", "")
            css_links = self.extract_links_from_css(css_content, page_url)
            links.update(css_links)

        # External stylesheets content (if accessible)
        for link_tag in soup.find_all("link", rel="stylesheet", href=True):
            stylesheet_url = self.normalize_url(link_tag["href"], page_url)
            if stylesheet_url:
                links.add(stylesheet_url)
                self.link_types[stylesheet_url] = "stylesheet"

        # 4. JavaScript content
        for script in soup.find_all("script"):
            if script.string:
                js_links = self.extract_links_from_javascript(script.string, page_url)
                links.update(js_links)

        # 5. Data attributes and custom attributes (more selective)
        for element in soup.find_all():
            for attr_name, attr_value in element.attrs.items():
                if isinstance(attr_value, str) and len(attr_value) > 0:
                    # Only look for attributes that are explicitly URL/link related
                    if attr_name.startswith("data-") and (
                        "url" in attr_name.lower()
                        or "link" in attr_name.lower()
                        or "href" in attr_name.lower()
                    ):
                        if self.is_valid_link(attr_value):
                            normalized = self.normalize_url(attr_value, page_url)
                            if normalized:
                                links.add(normalized)
                                self.link_types[normalized] = "data_attribute"

        # 6. Extract URLs from plain text content (be conservative)
        text_content = soup.get_text()
        url_pattern = re.compile(r'https?://[^\s<>"\']+', re.IGNORECASE)
        for match in url_pattern.finditer(text_content):
            url = match.group(0).rstrip(".,;!?)")  # Remove trailing punctuation
            if self.is_valid_link(url):
                links.add(url)
                self.link_types[url] = "text_content"

        # 7. Email and telephone links
        for match in self.email_pattern.finditer(str(soup)):
            email_url = match.group(0)
            links.add(email_url)
            self.link_types[email_url] = "email"

        for match in self.phone_pattern.finditer(str(soup)):
            phone_url = match.group(0)
            links.add(phone_url)
            self.link_types[phone_url] = "telephone"

        return links

    async def fetch_page(
        self, url: str
    ) -> tuple[Optional[str], Optional[BeautifulSoup]]:
        """Fetch and parse a page"""
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    content = await response.text()
                    soup = BeautifulSoup(content, "html.parser")
                    return content, soup
                logger.warning(f"Failed to fetch {url}: HTTP {response.status}")
                return None, None
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return None, None

    async def discover_pages(self) -> set[str]:
        """Discover all pages on the site"""
        pages_to_crawl = {self.base_url}
        discovered_pages = set()

        while pages_to_crawl:
            current_batch = list(pages_to_crawl)[:20]  # Process in batches
            pages_to_crawl -= set(current_batch)

            tasks = []
            for page_url in current_batch:
                if page_url not in discovered_pages:
                    tasks.append(self.fetch_page(page_url))

            if not tasks:
                continue

            results = await asyncio.gather(*tasks, return_exceptions=True)

            for i, result in enumerate(results):
                page_url = current_batch[i]

                if isinstance(result, Exception):
                    logger.error(f"Exception crawling {page_url}: {result}")
                    continue

                content, soup = result
                if soup is None:
                    continue

                discovered_pages.add(page_url)

                # Extract links from this page
                page_links = self.extract_comprehensive_links(soup, page_url)

                # Add internal pages for further crawling
                for link in page_links:
                    self.all_links.add(link)
                    self.link_sources[link].append(page_url)

                    # If it's an internal page we haven't seen, add it for crawling
                    if (
                        urlparse(link).netloc == self.domain
                        and link not in discovered_pages
                        and link not in pages_to_crawl
                        and not link.endswith(
                            (".pdf", ".jpg", ".jpeg", ".png", ".gif", ".css", ".js")
                        )
                    ):
                        pages_to_crawl.add(link)

        logger.info(f"Discovered {len(discovered_pages)} pages")
        return discovered_pages

    async def check_link(self, url: str) -> dict:
        """Check a single link with enhanced error handling"""
        start_time = time.time()

        try:
            async with self.session.head(url, allow_redirects=False) as response:
                response_time = time.time() - start_time

                if response.status in [200, 202, 204]:
                    return {
                        "url": url,
                        "status": "working",
                        "status_code": response.status,
                        "response_time": response_time,
                        "redirect_url": "",
                        "error_message": "",
                    }
                if response.status in [301, 302, 303, 307, 308]:
                    redirect_url = response.headers.get("Location", "")
                    if redirect_url:
                        redirect_url = self.normalize_url(redirect_url, url)

                    return {
                        "url": url,
                        "status": "redirect",
                        "status_code": response.status,
                        "response_time": response_time,
                        "redirect_url": redirect_url,
                        "error_message": "",
                    }
                return {
                    "url": url,
                    "status": "broken",
                    "status_code": response.status,
                    "response_time": response_time,
                    "redirect_url": "",
                    "error_message": f"HTTP {response.status}",
                }

        except asyncio.TimeoutError:
            return {
                "url": url,
                "status": "error",
                "status_code": None,
                "response_time": time.time() - start_time,
                "redirect_url": "",
                "error_message": "Timeout",
            }
        except Exception as e:
            return {
                "url": url,
                "status": "error",
                "status_code": None,
                "response_time": time.time() - start_time,
                "redirect_url": "",
                "error_message": str(e),
            }

    async def check_all_links(self) -> None:
        """Check all discovered links"""
        logger.info(f"Checking {len(self.all_links)} unique links...")

        # Convert to list for processing
        links_to_check = list(self.all_links)

        # Process in batches to avoid overwhelming servers
        batch_size = self.max_concurrent
        for i in range(0, len(links_to_check), batch_size):
            batch = links_to_check[i : i + batch_size]

            tasks = [self.check_link(url) for url in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Exception checking link: {result}")
                    continue

                # Categorize results
                status = result["status"]
                if status == "working":
                    self.results["working"].append(result)
                elif status == "broken":
                    self.results["broken"].append(result)
                elif status == "redirect":
                    self.results["redirects"].append(result)
                else:
                    self.results["errors"].append(result)

            # Progress indication
            if i + batch_size < len(links_to_check):
                logger.info(f"Checked {i + batch_size}/{len(links_to_check)} links...")

    def generate_enhanced_report(self) -> dict:
        """Generate comprehensive report with enhanced categorization"""
        total_links = len(self.all_links)
        working_count = len(self.results["working"])
        broken_count = len(self.results["broken"])
        redirect_count = len(self.results["redirects"])
        error_count = len(self.results["errors"])

        success_rate = (working_count / total_links * 100) if total_links > 0 else 0

        # Categorize broken links
        broken_categories = defaultdict(list)
        for result in self.results["broken"] + self.results["errors"]:
            url = result["url"]
            link_type = self.link_types.get(url, "unknown")

            if urlparse(url).netloc == self.domain:
                category = "internal_broken"
            elif "investvegan.org" in url:
                category = "investvegan_broken"
            elif result["status_code"] == 404:
                category = "external_404"
            elif "dns" in result.get("error_message", "").lower():
                category = "dns_error"
            elif result["status_code"] in [403, 401]:
                category = "access_denied"
            else:
                category = "other_broken"

            broken_categories[category].append(
                {
                    "url": url,
                    "type": link_type,
                    "error": result.get("error_message", ""),
                    "status_code": result.get("status_code"),
                    "found_on": self.link_sources.get(url, [])[:3],  # First 3 pages
                    "context": self.link_contexts.get(url, {}),
                }
            )

        # Create comprehensive report
        report = {
            "summary": {
                "site_url": self.base_url,
                "crawl_timestamp": datetime.now().isoformat(),
                "pages_crawled": len(self.pages_crawled),
                "unique_links_found": total_links,
                "working_links": working_count,
                "broken_links": broken_count,
                "redirect_links": redirect_count,
                "error_links": error_count,
                "success_rate": round(success_rate, 1),
            },
            "link_categories": {
                "by_type": dict(Counter(self.link_types.values())),
                "by_domain": self._categorize_by_domain(),
            },
            "broken_link_categories": dict(broken_categories),
            "detailed_results": {
                "working": self.results["working"],
                "broken": self.results["broken"],
                "redirects": self.results["redirects"],
                "errors": self.results["errors"],
            },
        }

        return report

    def _categorize_by_domain(self) -> dict[str, int]:
        """Categorize links by domain"""
        domain_counts = defaultdict(int)

        for url in self.all_links:
            domain = urlparse(url).netloc or "special_schemes"
            domain_counts[domain] += 1

        return dict(domain_counts)

    async def run_comprehensive_check(self) -> dict:
        """Run the complete enhanced link checking process"""
        start_time = time.time()

        logger.info(f"Starting enhanced comprehensive link check for {self.base_url}")

        # Step 1: Discover all pages
        self.pages_crawled = await self.discover_pages()

        # Step 2: Check all discovered links
        await self.check_all_links()

        execution_time = time.time() - start_time

        # Step 3: Generate report
        report = self.generate_enhanced_report()
        report["summary"]["execution_time_seconds"] = round(execution_time, 1)

        logger.info(f"Link check completed in {execution_time:.1f} seconds")
        logger.info(
            f"Found {len(self.all_links)} unique links across {len(self.pages_crawled)} pages"
        )
        logger.info(
            f"Results: {len(self.results['working'])} working, {len(self.results['broken'])} broken, {len(self.results['redirects'])} redirects"
        )

        return report


# Import Counter for report generation
from collections import Counter


async def main():
    """Main execution function"""
    base_url = "https://ethicic.com"

    async with EnhancedLinkChecker(base_url, max_concurrent=8) as checker:
        report = await checker.run_comprehensive_check()

        # Save detailed JSON report
        with open("enhanced_link_report.json", "w") as f:
            json.dump(report, f, indent=2, default=str)

        # Generate markdown summary
        generate_markdown_summary(report)

        return report


def generate_markdown_summary(report: dict) -> None:
    """Generate a concise markdown summary report"""
    summary = report["summary"]
    broken_categories = report["broken_link_categories"]

    markdown_content = f"""# Enhanced Link Check Report - ethicic.com

**Generated**: {datetime.now().strftime('%Y-%m-%d at %I:%M %p %Z')}
**Execution Time**: {summary['execution_time_seconds']} seconds

## 📊 Summary
- **Pages Crawled**: {summary['pages_crawled']}
- **Total Unique Links**: {summary['unique_links_found']}
- **Working Links**: {summary['working_links']} ({summary['success_rate']}%)
- **Broken Links**: {summary['broken_links']}
- **Redirects**: {summary['redirect_links']}
- **Errors**: {summary['error_links']}

## 🚨 Critical Issues by Category

### Internal Site Issues ({len(broken_categories.get('internal_broken', []))})
"""

    # Add internal broken links
    for link in broken_categories.get("internal_broken", [])[:10]:  # Top 10
        markdown_content += f"- ❌ `{link['url']}` - {link['error']}\n"

    markdown_content += f"""
### External Domain Issues

#### Investvegan.org Problems ({len(broken_categories.get('investvegan_broken', []))})
All references to the defunct investvegan.org domain are failing.

#### Other External Issues ({len(broken_categories.get('external_404', [])) + len(broken_categories.get('dns_error', [])) + len(broken_categories.get('access_denied', []))})
- 404 Not Found: {len(broken_categories.get('external_404', []))}
- DNS Errors: {len(broken_categories.get('dns_error', []))}
- Access Denied: {len(broken_categories.get('access_denied', []))}

## 📈 Link Distribution
"""

    # Add link type distribution
    if "link_categories" in report:
        markdown_content += "\n### By Link Type:\n"
        for link_type, count in report["link_categories"]["by_type"].items():
            markdown_content += f"- {link_type}: {count}\n"

        markdown_content += "\n### By Domain (Top 10):\n"
        domain_counts = sorted(
            report["link_categories"]["by_domain"].items(),
            key=lambda x: x[1],
            reverse=True,
        )[:10]
        for domain, count in domain_counts:
            markdown_content += f"- {domain}: {count}\n"

    markdown_content += """
## 🎯 Next Steps
1. **Fix internal 404s** - Critical for user experience
2. **Address investvegan.org references** - Remove or replace with alternatives
3. **Review external link dependencies** - Update or remove broken external links

**Full JSON Report**: `enhanced_link_report.json`
"""

    with open("ENHANCED_LINK_CHECK_REPORT.md", "w") as f:
        f.write(markdown_content)

    print("✅ Enhanced link check completed!")
    print("📄 Summary report: ENHANCED_LINK_CHECK_REPORT.md")
    print("📊 Detailed data: enhanced_link_report.json")


if __name__ == "__main__":
    asyncio.run(main())
