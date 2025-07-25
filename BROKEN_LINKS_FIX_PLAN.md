# 🔧 Broken Links Fix Plan - Ethicic.com
**Based on Exhaustive Link Analysis - July 24, 2025**

---

## 📋 Overview
This plan addresses the 100 broken links identified in our comprehensive site crawl. Each fix is categorized by type and priority, with specific implementation details.

**Total Broken Links**: 100
**Critical Internal Issues**: 20+
**External Domain Issues**: 40+ (mostly investvegan.org)
**Malformed URLs**: 5+

---

## 🚨 PRIORITY 1: Critical Internal Page Fixes

### **1.1 Add Form ADV Redirect** ✅ **CONFIRMED BY USER**
```python
# Add to public_site/urls.py
path(
    "disclosures/form-adv/",
    RedirectView.as_view(
        url="https://reports.adviserinfo.sec.gov/reports/ADV/316032/PDF/316032.pdf",
        permanent=True
    ),
    name="redirect_form_adv",
),
```

### **1.2 Missing Critical Pages** ⚠️ **NEEDS USER DECISION**

#### **A. Research Page (`/research/` - 404)**
**Options:**
1. **Create dedicated research page** with content about your research methodology
2. **Redirect to blog section** (`/blog/` - where research content lives)
3. **Redirect to strategies section** (`/strategies/` - investment research)
4. **Remove references** to /research/ from navigation/content

**Recommendation**: Redirect to `/blog/` since that's where your research content appears to be.
THIS IS APPROVED -- REDIRECT TO BLOG

#### **B. Sitemap XML (`/sitemap.xml` - 404)** 🚨 **SEO CRITICAL**
**Solution**: Django/Wagtail should auto-generate this. Need to:
1. **Check if Wagtail sitemaps are enabled** in settings
2. **Add sitemap framework** if missing
3. **Generate XML sitemap** for SEO

**Implementation**:
```python
# Add to ethicic/urls.py
from django.contrib.sitemaps.views import sitemap
from wagtail.contrib.sitemaps import Sitemap

urlpatterns = [
    # ... existing patterns
    path('sitemap.xml', sitemap, {'sitemaps': {'wagtail': Sitemap}}, name='sitemap'),
]
```

THIS IS APPROVED -- GENERATE THE SITEMAP.


#### **C. PRI DDQ Page (`/pri-ddq/` - 404)**
**Options:**
1. **Create PRI DDQ page** with your DDQ information
2. **Redirect to disclosures page** (`/disclosures/`)
3. **Redirect to contact page** for DDQ requests
4. **Create downloadable PDF** and redirect to it

**Need User Input**: What should happen when someone visits `/pri-ddq/`?

WE HAVE A PAGE FOR THIS ALREADY

#### **D. Performance Page (`/performance/` - 404)**
**Analysis**: You mentioned performance data lives on strategy pages.
**Options:**
1. **Redirect to strategies section** (`/strategies/`)
2. **Create performance overview page** that links to individual strategy performance
3. **Redirect to specific strategy** (e.g., `/strategies/growth/`)

**Recommendation**: Redirect to `/strategies/` since that's where performance data lives.

JUST DELETE ALL REFERENCES TO THE /PERFORMANCE PAGE

### **1.3 Broken Blog Posts** ⚠️ **NEEDS USER DECISION**

These blog posts are referenced but return 404:
- `/blog/how-i-became-an-active-manager/`
- `/blog/what-does-inflation-mean-to-you/`
- `/blog/what-should-you-expect-when-youre-investing/`

**Options:**
1. **Restore posts** if they exist in CMS but aren't published
2. **Remove references** from navigation/content
3. **Create redirects** to similar content
4. **Archive and redirect** to blog index

**Need User Input**: Should these posts be restored, removed, or redirected?

THE POSTS SHOULD BE PUBLISHED -- INVESTIGATE WHY THE PAGES ARE NOT WORKING PROPERLY.

### **1.4 Broken Internal Process/Form Links**

#### **Missing Process Sub-pages:**
- `/our-process/screening/` → **Redirect to** `/process/` ?
CHANGE REFERENCES TO POINT TO JUST /PROCESS
- `/reach-out/` → **Redirect to** `/contact/`
GOOD PLAN
- `/charitable-giving-resources/` → **Create page or redirect** ?
THIS IS A BLOG POST THAT SHOULD EXIST

#### **Missing Form Library:**
- `/form-library/account-transfer-form/` → **Redirect to** `/contact/` or `/onboarding/` ?
- `/form-library/ask-a-question/` → **Redirect to** `/contact/` ?

**Need User Input**: Where should these process and form links redirect?
WE'RE NOT DOING THE FORM REFERENCE THNG ANYMORE


---

## 🚨 PRIORITY 2: External Domain Issues

### **2.1 InvestVegan.org Dependency (40+ broken links)**

**Problem**: All `https://investvegan.org/*` links are failing (DNS/domain issues)

**Affected Content:**
- Blog posts reference investvegan.org articles
- Images hosted on investvegan.org
- External links to investvegan.org resources

**Options:**
1. **Remove all references** to investvegan.org
2. **Replace with archived versions** using archive.org
3. **Replace with alternative resources** covering same topics
4. **Update content** to remove external dependencies

**Recommendation**: Remove references and update content to be self-contained.

EACH OF THESE RESOURCES SHOULD EXIST ON OUR SITE ALREADY. WORK THROUGH THEM MANUALLY AND FIND ISUES.

**Implementation**: Search and replace across templates/content:
```bash
# Find all references
grep -r "investvegan.org" templates/ static/
# Replace or remove based on context
```

### **2.2 Other External Link Issues**
- Some social media links returning 403/404
- Academic links with access restrictions
- **Action**: Audit and update/remove broken external links

KEEP ACADEMIC LINKS WITH ACCESS RESTRICTIONS. INVESTIGATE AND CATALOG THE BROKEN SOCIAL LINKS

---

## 🚨 PRIORITY 3: Technical & Malformed URLs

### **3.1 Malformed URLs in Content**
- `http://Issued public` → **Remove or fix**
- Incorrect mailto: formatting → **Fix email links**
- Incorrect tel: formatting → **Fix phone links**

APPROVED

### **3.2 Broken Internal Links**
Various internal links that need redirects or content creation:
- `/strategies/global-opportunitites/` (typo?) → `/strategies/growth/` ?
- `/dont-stop-with-divestment/` → Blog post?
- `/our-investment-beliefs-and-competitive-advantages/` → `/about/` ?

FIX THESE EACH MANUALLY, ASKING FOR APPROVAL AS YOU GO.

---

## 📋 PROPOSED IMPLEMENTATION PLAN

### **Phase 1: Immediate Fixes (No Content Changes)**
```python
# Add these redirects to public_site/urls.py:

# Form ADV (confirmed by user)
path("disclosures/form-adv/", RedirectView.as_view(
    url="https://reports.adviserinfo.sec.gov/reports/ADV/316032/PDF/316032.pdf",
    permanent=True), name="redirect_form_adv"),

# Performance page → strategies
path("performance/", RedirectView.as_view(
    url="/strategies/", permanent=True), name="redirect_performance"),

# Process screening → main process
path("our-process/screening/", RedirectView.as_view(
    url="/process/", permanent=True), name="redirect_screening"),

# Reach out → contact
path("reach-out/", RedirectView.as_view(
    url="/contact/", permanent=True), name="redirect_reach_out"),

# Form library → contact or onboarding
path("form-library/account-transfer-form/", RedirectView.as_view(
    url="/contact/", permanent=True), name="redirect_transfer_form"),
path("form-library/ask-a-question/", RedirectView.as_view(
    url="/contact/", permanent=True), name="redirect_ask_question"),

# Fix typo in strategies
path("strategies/global-opportunitites/", RedirectView.as_view(
    url="/strategies/growth/", permanent=True), name="redirect_typo_fix"),
```

### **Phase 2: Content Cleanup**
1. **Search and remove** investvegan.org references
2. **Fix malformed URLs** in content
3. **Clean up** broken internal references

### **Phase 3: SEO & Technical**
1. **Enable sitemap.xml** generation
2. **Audit remaining** external links
3. **Set up monitoring** for future broken links

---

## ❓ QUESTIONS FOR USER APPROVAL

Before implementing any fixes, I need your decisions on:

### **Critical Page Routing:**
1. **Research page** (`/research/`) → Redirect to `/blog/` or create dedicated page?
2. **PRI DDQ page** (`/pri-ddq/`) → What should this show/redirect to?
3. **Broken blog posts** → Restore, remove references, or redirect?
4. **Charitable giving resources** → Create page or redirect somewhere?

### **Content Strategy:**
5. **InvestVegan.org references** → Remove all, replace with archive.org, or update content?
6. **Form library links** → All redirect to `/contact/`, or different destinations?

### **Technical Priorities:**
7. **Sitemap.xml** → Enable Wagtail auto-generation?
8. **Process sub-pages** → All redirect to main `/process/` page?

---

## 🎯 EXPECTED OUTCOMES

After implementing this plan:
- **Eliminate all internal 404s** (improve from 76.1% to 90%+ success rate)
- **Fix SEO issues** (sitemap, internal linking)
- **Clean up external dependencies** (reduce maintenance burden)
- **Improve user experience** (no more broken navigation)

**Please review this plan and let me know your preferences for the questions above, then I'll implement the approved fixes.**
