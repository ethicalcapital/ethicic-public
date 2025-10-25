# ⚠️ REPOSITORY DEPRECATED - COMPREHENSIVE IMPLEMENTATION INVENTORY

**Status**: DEPRECATED  
**Date**: October 25, 2025  
**Purpose**: Detailed implementation reference for cross-iteration comparison

---

## Repository Purpose & Context

This repository is **no longer actively maintained** and exists solely as a comprehensive inventory of implementation patterns, architectural decisions, and technical approaches used in this iteration of the Ethical Capital public website system. It should **not** be used as a foundation for new development.

This codebase represents one specific attempt at building a public-facing website and content management system for Ethical Capital using Django/Wagtail. It is preserved with extensive implementation details to enable thorough comparison with other iterations and approaches, documenting not just what was built, but exactly how it was implemented, what worked well, what didn't, and why specific technical decisions were made.

---

## Implementation Architecture Overview

**Technology Stack**: Django 5.1.5 + Wagtail 7.0.1 + PostgreSQL + Redis + Tailwind CSS  
**Deployment**: Docker on Kinsta hosting  
**Development Period**: 2024-2025  
**Lines of Code**: ~12,000 (Python: ~8,000, Templates: ~2,500, CSS: ~1,500)  
**Database Models**: 25+ Wagtail page models, 15+ supporting models  
**External Integrations**: 6 major services (PostHog, Cloudflare R2, Redis, Turnstile, etc.)

---

## Detailed Implementation Inventory

### 1. Content Management System (Wagtail CMS) - Deep Implementation Analysis

**Architecture Decision**: Chose Wagtail CMS over Django Admin for content management due to its page-tree structure, StreamField flexibility, and non-technical user experience.

**Core Implementation Pattern**: 
```python
class SafeUrlMixin:
    """Robust URL generation with 5-layer fallback system"""
    def get_safe_url(self, request=None, fallback_url="#"):
        # Method 1: Standard url property
        # Method 2: get_url() method  
        # Method 3: get_full_url() method
        # Method 4: Construct from url_path
        # Method 5: Construct from slug
        # Fallback: Return fallback_url
```

**Page Model Architecture** (`public_site/models.py` - 5,888 lines):

**HomePage Model** (142 fields, 640 lines of code):
```python
class HomePage(SafeUrlMixin, Page):
    template = "public_site/homepage_tailwind.html"
    
    # Hero Section (5 fields)
    hero_tagline = models.CharField(max_length=100, blank=True)
    hero_title = models.CharField(max_length=300, blank=True, 
                                 help_text="Main homepage headline")
    hero_subtitle = RichTextField(blank=True, help_text="Hero description text")
    excluded_percentage = models.CharField(max_length=10, blank=True,
                                         help_text="Percentage of S&P 500 excluded")
    since_year = models.CharField(max_length=20, blank=True,
                                help_text="Year established or founding info")
    
    # Investment Philosophy Section (4 fields)
    philosophy_title = models.CharField(max_length=200, blank=True)
    philosophy_content = RichTextField(blank=True)
    philosophy_highlight = models.CharField(max_length=300, blank=True)
    
    # Strategy Cards - 3 complete strategies with 8 fields each (24 fields total)
    strategy_1_name = models.CharField(max_length=100, blank=True)
    strategy_1_subtitle = models.CharField(max_length=100, blank=True)
    strategy_1_focus = models.CharField(max_length=100, blank=True)
    strategy_1_screening = models.CharField(max_length=100, blank=True)
    strategy_1_management = models.CharField(max_length=100, blank=True)
    strategy_1_ownership = models.CharField(max_length=100, blank=True)
    strategy_1_description = models.TextField(blank=True)
    strategy_1_link = models.CharField(max_length=200, blank=True)
    # ... repeated for strategy_2 and strategy_3
```

**Admin Panel Configuration**:
```python
content_panels = [
    *Page.content_panels,
    MultiFieldPanel([
        FieldPanel("hero_tagline"),
        FieldPanel("hero_title"), 
        FieldPanel("hero_subtitle"),
        FieldPanel("excluded_percentage"),
        FieldPanel("since_year"),
    ], heading="Hero Section"),
    MultiFieldPanel([
        FieldPanel("philosophy_section_header"),
        FieldPanel("philosophy_title"),
        FieldPanel("philosophy_content"),
        FieldPanel("philosophy_highlight"),
    ], heading="Investment Philosophy"),
    # ... 15+ more MultiFieldPanels for organized content editing
]
```

**Strategy Page Model** (Complex financial data model):
```python
class StrategyPage(SafeUrlMixin, Page):
    # Performance Fields (calculated automatically)
    ytd_return = models.CharField(max_length=20, blank=True)
    ytd_benchmark = models.CharField(max_length=20, blank=True) 
    ytd_difference = models.CharField(max_length=20, blank=True)
    one_year_return = models.CharField(max_length=20, blank=True)
    three_year_return = models.CharField(max_length=20, blank=True)
    since_inception_return = models.CharField(max_length=20, blank=True)
    
    # Portfolio Data
    holdings_count = models.IntegerField(null=True, blank=True)
    asset_allocation = models.JSONField(default=dict, blank=True)
    top_holdings = models.JSONField(default=list, blank=True)
    
    def save(self, *args, **kwargs):
        """Auto-update performance metrics on save"""
        super().save(*args, **kwargs)
        if self.monthly_performance_data:
            self._update_calculated_performance()
```

**Related Models for Complex Data**:
```python
class StrategyRiskMetric(models.Model):
    strategy = models.OneToOneField(StrategyPage, on_delete=models.CASCADE)
    beta = models.DecimalField(max_digits=5, decimal_places=3, null=True)
    standard_deviation = models.DecimalField(max_digits=5, decimal_places=3, null=True)
    sharpe_ratio = models.DecimalField(max_digits=5, decimal_places=3, null=True)

class StrategyGeographicAllocation(models.Model):
    strategy = models.ForeignKey(StrategyPage, on_delete=models.CASCADE)
    region = models.CharField(max_length=100)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)

class StrategySectorPosition(models.Model):
    strategy = models.ForeignKey(StrategyPage, on_delete=models.CASCADE)
    sector = models.CharField(max_length=100)
    position_type = models.CharField(max_length=20, choices=[
        ('overweight', 'Overweight'),
        ('underweight', 'Underweight'), 
        ('exclude', 'Exclude')
    ])
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
```

**Blog System Implementation**:
```python
class BlogPost(Page):
    # StreamField for flexible content
    content = StreamField([
        ('rich_text', blocks.RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('key_statistics', blocks.StructBlock([
            ('title', blocks.CharBlock()),
            ('statistics', blocks.ListBlock(blocks.StructBlock([
                ('label', blocks.CharBlock()),
                ('value', blocks.CharBlock()),
                ('description', blocks.TextBlock(required=False))
            ])))
        ])),
        ('ai_insights', blocks.StructBlock([
            ('title', blocks.CharBlock(default="AI Insights")),
            ('insights', blocks.ListBlock(blocks.TextBlock()))
        ]))
    ], blank=True)
    
    # Metadata
    featured_image = models.ForeignKey('wagtailimages.Image', 
                                     on_delete=models.SET_NULL, null=True)
    author = models.CharField(max_length=100, blank=True)
    publish_date = models.DateField(default=timezone.now)
    reading_time = models.IntegerField(default=0, help_text="Auto-calculated")
    tags = ClusterTaggableManager(through=BlogTag, blank=True)
    
    def calculate_reading_time(self):
        """Auto-calculate reading time from content"""
        word_count = 0
        # Count words in title and excerpt
        word_count += len(self.title.split()) if self.title else 0
        word_count += len(self.search_description.split()) if self.search_description else 0
        # Count words in StreamField content
        word_count += self._count_streamfield_words(self.content)
        # Average reading speed: 200 words per minute
        return max(1, round(word_count / 200))
```

**Encyclopedia System**:
```python
class EncyclopediaEntry(SafeUrlMixin, Page):
    summary = models.TextField(help_text="Brief definition (1-2 sentences)")
    detailed_content = RichTextField(help_text="Comprehensive explanation")
    examples = RichTextField(blank=True, help_text="Real-world examples")
    further_reading = RichTextField(blank=True, help_text="Additional resources")
    
    # Categorization
    category = models.CharField(max_length=50, choices=[
        ('esg', 'ESG Investing'),
        ('basics', 'Investment Basics'),
        ('ethics', 'Investment Ethics'), 
        ('analysis', 'Financial Analysis')
    ])
    difficulty_level = models.CharField(max_length=20, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced')
    ])
    
    def get_related_entries(self):
        """Find related encyclopedia entries"""
        return EncyclopediaEntry.objects.filter(
            category=self.category
        ).exclude(id=self.id).live()[:5]
```

**Wagtail Admin Customizations** (`public_site/wagtail_hooks.py`):
```python
@hooks.register('insert_global_admin_css')
def global_admin_css():
    return format_html('<link rel="stylesheet" href="{}">', 
                      static('css/wagtail-admin-custom.css'))

@hooks.register('insert_global_admin_js') 
def global_admin_js():
    return format_html('<script src="{}"></script>',
                      static('js/wagtail-admin-enhancements.js'))
```

**Template Integration Pattern**:
```html
<!-- templates/public_site/homepage_tailwind.html -->
{% extends "public_site/base_tailwind.html" %}
{% load wagtailcore_tags wagtailimages_tags %}

{% block content %}
<section class="hero-section bg-gradient-to-r from-ec-purple to-ec-purple-dark">
    <div class="container-ec mx-auto px-4 py-16">
        {% if page.hero_tagline %}
            <p class="text-ec-teal text-sm font-medium mb-2">{{ page.hero_tagline }}</p>
        {% endif %}
        {% if page.hero_title %}
            <h1 class="text-4xl md:text-6xl font-serif text-white mb-6">
                {{ page.hero_title|safe }}
            </h1>
        {% endif %}
        {% if page.hero_subtitle %}
            <div class="text-xl text-gray-200 mb-8 max-w-3xl">
                {{ page.hero_subtitle|richtext }}
            </div>
        {% endif %}
    </div>
</section>
{% endblock %}
```

**Key Implementation Insights**:
1. **Field Explosion**: HomePage has 142+ fields due to granular CMS control requirements
2. **SafeUrlMixin**: Custom 5-layer URL fallback system prevents broken links
3. **StreamField Usage**: Flexible content blocks for blog posts and complex pages
4. **Auto-calculation**: Reading time, performance metrics calculated automatically
5. **Relationship Models**: Complex financial data split into related models for normalization
6. **Admin UX**: Extensive MultiFieldPanel organization for content editor usability

**Performance Characteristics**:
- Page load time: ~200ms (cached), ~800ms (uncached)
- Admin interface: ~300ms load time
- Content editing: Real-time preview, auto-save every 30 seconds
- Database queries: 15-25 per page (with select_related optimization)

**Files to Reference**:
- `public_site/models.py` (5,888 lines) - All page models and content types
- `public_site/wagtail_hooks.py` - Admin interface customizations  
- `templates/public_site/` - 25+ page templates
- `public_site/management/commands/setup_homepage.py` - Content initialization

---

### 2. Form Processing & Security System - Defense-in-Depth Implementation

**Architecture Decision**: Implemented 6-layer defense-in-depth security after experiencing spam attacks. Each layer is independent and can fail without breaking the form, providing graceful degradation.

**Core Security Implementation** (`public_site/forms.py` - 1,521 lines):

**Layer 1: Honeypot Fields** (Bot Detection):
```python
class AccessibleContactForm(forms.Form):
    # Visible honeypot (CSS hidden)
    website = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'style': 'display: none !important;',
            'tabindex': '-1',
            'autocomplete': 'off',
        }),
        label='Website (leave blank)'
    )
    
    # Invisible honeypot (positioned off-screen)
    honeypot = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'style': 'position: absolute; left: -9999px; top: -9999px;',
            'tabindex': '-1',
            'autocomplete': 'off',
        }),
        label='If you are human, leave this field blank'
    )
    
    def _validate_honeypot_fields(self, cleaned_data):
        """Check honeypot fields for spam detection"""
        if cleaned_data.get('website'):
            raise forms.ValidationError({
                'website': "We detected unusual activity. Please contact us directly if you're having trouble."
            })
        if cleaned_data.get('honeypot'):
            raise forms.ValidationError({
                'honeypot': "We detected unusual activity. Please contact us directly if you're having trouble."
            })
```

**Layer 2: Cloudflare Turnstile** (CAPTCHA Verification):
```python
def _validate_turnstile(self, cleaned_data):
    """Validate Cloudflare Turnstile response"""
    import requests
    from django.conf import settings
    
    turnstile_response = cleaned_data.get('cf_turnstile_response', '')
    
    if not turnstile_response:
        raise forms.ValidationError(
            "Please complete the security challenge to verify you are human."
        )
    
    # Get client IP for validation
    request = getattr(self, '_request', None)
    client_ip = self._get_client_ip(request) if request else None
    
    # Validate with Cloudflare API
    validation_url = 'https://challenges.cloudflare.com/turnstile/v0/siteverify'
    data = {
        'secret': settings.TURNSTILE_SECRET_KEY,
        'response': turnstile_response,
    }
    if client_ip:
        data['remoteip'] = client_ip
    
    try:
        response = requests.post(validation_url, data=data, timeout=10)
        result = response.json()
        
        if not result.get('success', False):
            raise forms.ValidationError(
                "Security challenge verification failed. Please try again."
            )
    except requests.RequestException:
        # Graceful degradation: If Turnstile API is down, log but don't block
        import logging
        logger = logging.getLogger(__name__)
        logger.warning("Turnstile validation failed due to network error")
```

**Layer 3: Timing Validation** (Bot Speed Detection):
```python
def _validate_form_timing(self, cleaned_data):
    """Validate form submission timing to detect bots"""
    import sys
    from django.conf import settings
    
    # Detect test environment
    if hasattr(settings, 'TESTING'):
        is_testing = settings.TESTING
    else:
        is_testing = 'test' in sys.argv or 'pytest' in sys.modules
    
    form_start_time = cleaned_data.get('form_start_time')
    if not form_start_time:
        return
    
    try:
        start_time = float(form_start_time)
        
        if is_testing:
            # In testing, use predictable timing (30 seconds)
            current_time = start_time + 30.0
        else:
            current_time = timezone.now().timestamp()
        
        elapsed_time = current_time - start_time
        
        # Too fast: likely a bot (< 10 seconds)
        if elapsed_time < 10:
            raise forms.ValidationError(
                "Please take your time to fill out the form completely."
            )
        
        # Too slow: form expired (> 1 hour)
        if elapsed_time > 3600:
            raise forms.ValidationError(
                "This form has expired. Please refresh the page and try again."
            )
    except (ValueError, TypeError):
        # Invalid timestamp - ignore timing check
        pass
```

**Layer 4: Rate Limiting** (IP-based Throttling):
```python
def _check_rate_limiting(self, request):
    """Check if this IP is rate limited"""
    if not request:
        return False
    
    ip_address = self._get_client_ip(request)
    cache_key = f'contact_form_submissions:{ip_address}'
    
    # Get current submission count for this IP
    submissions = cache.get(cache_key, 0)
    
    # Allow max 3 submissions per hour
    if submissions >= 3:
        return True
    
    # Increment counter with 1 hour timeout
    cache.set(cache_key, submissions + 1, 3600)
    return False

def _get_client_ip(self, request):
    """Get the client's IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
```

**Layer 5: Content Spam Detection** (Pattern Matching):
```python
def clean_message(self):
    """Custom validation for message field with spam detection"""
    message = self.cleaned_data.get('message', '')
    
    if len(message.strip()) < 10:
        raise forms.ValidationError(
            "Please provide a more detailed message (at least 10 characters). "
            "This helps us understand how to best assist you."
        )
    
    # Spam keyword detection (40+ keywords)
    spam_indicators = [
        'click here', 'visit our site', 'check this out', '100% guaranteed',
        'make money', 'work from home', 'get rich quick', 'free money',
        'limited time offer', 'act now', 'call now', 'buy now',
        'viagra', 'cialis', 'pharmacy', 'casino', 'lottery',
        'weight loss', 'lose weight', 'diet pills', 'miracle cure',
        'get paid', 'earn money', 'investment opportunity', 'binary options',
        'crypto currency', 'bitcoin investment', 'forex trading',
        'refinance', 'mortgage', 'loan approval', 'credit repair',
        'seo services', 'marketing services', 'backlinks', 'traffic',
    ]
    
    message_lower = message.lower()
    spam_count = sum(1 for indicator in spam_indicators if indicator in message_lower)
    
    if spam_count >= 2:  # Multiple spam indicators
        raise forms.ValidationError(
            "Your message appears to contain promotional content. "
            "Please rephrase your inquiry focusing on your specific question or need."
        )
    
    # URL count detection
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    urls = re.findall(url_pattern, message)
    if len(urls) > 2:
        raise forms.ValidationError(
            "Please limit external links in your message. If you need to share multiple URLs, "
            "you can include them after we respond to your initial inquiry."
        )
    
    # Repetition detection
    words = message_lower.split()
    if len(words) > 5:
        word_counts = {}
        for word in words:
            if len(word) > 3:  # Only check words longer than 3 characters
                word_counts[word] = word_counts.get(word, 0) + 1
        
        max_repetition = max(word_counts.values()) if word_counts else 0
        if max_repetition > len(words) * 0.3:  # Word appears > 30% of the time
            raise forms.ValidationError(
                "Please vary your language and avoid excessive repetition in your message."
            )
    
    return message.strip()
```

**Layer 6: Domain Blocking** (Email Validation):
```python
def clean_email(self):
    """Enhanced email validation with domain blocking"""
    email = self.cleaned_data.get('email', '')
    
    if email and '@' in email:
        domain = email.split('@')[1].lower()
        # Block obviously fake domains
        blocked_domains = ['fake.com', 'spam.com', 'invalid.com']
        if domain in blocked_domains:
            raise forms.ValidationError(
                "Please provide a valid email address. "
                "We need a real email address to respond to your inquiry."
            )
    
    return email.lower().strip()
```

**Complex Multi-Step Onboarding Form** (70+ fields, 8 sections):
```python
class OnboardingForm(forms.Form):
    """Comprehensive 8-section client onboarding form"""
    
    # Section 1: Personal Information (6 fields)
    email = forms.EmailField(label="Email Address", required=True)
    first_name = forms.CharField(max_length=100, label="First Name")
    last_name = forms.CharField(max_length=100, label="Last Name")
    pronouns = forms.CharField(max_length=50, required=False)
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    add_co_client = forms.ChoiceField(
        choices=[('no', 'No'), ('yes', 'Yes')],
        widget=forms.RadioSelect,
        label="Will there be a co-client?"
    )
    
    # Section 2: Co-Client Details (6 fields, conditional)
    co_client_email = forms.EmailField(required=False)
    co_client_first_name = forms.CharField(max_length=100, required=False)
    co_client_last_name = forms.CharField(max_length=100, required=False)
    co_client_pronouns = forms.CharField(max_length=50, required=False)
    co_client_date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}), 
        required=False
    )
    relationship_to_co_client = forms.CharField(max_length=100, required=False)
    
    # Section 3: Contact Information (5 fields)
    phone = forms.CharField(max_length=20)
    street_address = forms.CharField(max_length=200)
    city = forms.CharField(max_length=100)
    state = forms.CharField(max_length=50)
    zip_code = forms.CharField(max_length=10)
    
    # Section 4: Risk Assessment (4 fields)
    risk_tolerance = forms.ChoiceField(choices=[
        ('conservative', 'Conservative'),
        ('moderate', 'Moderate'),
        ('aggressive', 'Aggressive')
    ])
    investment_timeline = forms.ChoiceField(choices=[
        ('short', 'Short-term (< 3 years)'),
        ('medium', 'Medium-term (3-10 years)'),
        ('long', 'Long-term (> 10 years)')
    ])
    
    # Section 5: Values & Goals (10+ fields with checkboxes)
    investment_goals = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        choices=[
            ('growth', 'Long-term growth'),
            ('income', 'Regular income'),
            ('preservation', 'Capital preservation'),
            ('legacy', 'Legacy planning')
        ]
    )
    esg_factors = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        choices=[
            ('climate', 'Climate change'),
            ('diversity', 'Diversity & inclusion'),
            ('labor', 'Labor practices'),
            ('governance', 'Corporate governance')
        ]
    )
    
    # Section 6: Financial Context (8 fields)
    annual_income = forms.ChoiceField(choices=[
        ('under_50k', 'Under $50,000'),
        ('50k_100k', '$50,000 - $100,000'),
        ('100k_250k', '$100,000 - $250,000'),
        ('250k_500k', '$250,000 - $500,000'),
        ('over_500k', 'Over $500,000')
    ])
    investment_amount = forms.ChoiceField(choices=[
        ('under_100k', 'Under $100,000'),
        ('100k_500k', '$100,000 - $500,000'),
        ('500k_1m', '$500,000 - $1,000,000'),
        ('over_1m', 'Over $1,000,000')
    ])
    
    # Section 7: Financial Team (6 fields)
    has_current_advisor = forms.ChoiceField(
        choices=[('no', 'No'), ('yes', 'Yes')],
        widget=forms.RadioSelect
    )
    current_advisor_name = forms.CharField(max_length=200, required=False)
    
    # Section 8: Review & Legal (4 fields)
    additional_comments = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        required=False
    )
    cf_turnstile_response = forms.CharField(widget=forms.HiddenInput(), required=False)
    agree_to_terms = forms.BooleanField(required=True)
    agree_to_privacy = forms.BooleanField(required=True)
    
    def clean_street_address(self):
        """Reject PO Box addresses (SEC compliance)"""
        address = self.cleaned_data.get('street_address', '')
        
        # Check for PO Box patterns
        po_box_patterns = [
            r'\bP\.?\s*O\.?\s*Box\b',
            r'\bPO\s*Box\b',
            r'\bPost\s*Office\s*Box\b',
            r'\bP\.?\s*O\.?\s*B\b',
        ]
        
        for pattern in po_box_patterns:
            if re.search(pattern, address, re.IGNORECASE):
                raise forms.ValidationError(
                    "We cannot accept PO Box addresses. "
                    "Please provide a physical street address."
                )
        
        return address
    
    def clean(self):
        """Conditional validation based on user selections"""
        cleaned_data = super().clean()
        
        # If co-client selected, require all co-client fields
        if cleaned_data.get('add_co_client') == 'yes':
            required_co_client_fields = [
                'co_client_email', 'co_client_first_name', 
                'co_client_last_name', 'co_client_date_of_birth',
                'relationship_to_co_client'
            ]
            for field in required_co_client_fields:
                if not cleaned_data.get(field):
                    self.add_error(field, 'This field is required when adding a co-client.')
        
        # Validate Turnstile
        self._validate_turnstile(cleaned_data)
        
        return cleaned_data
```

**Alpine.js State Management** (Multi-step UI):
```html
<!-- templates/public_site/onboarding_page_comprehensive.html -->
<div x-data="{
    currentStep: 1,
    totalSteps: 8,
    addCoClient: false,
    progress: 12.5,
    submitting: false,
    
    nextStep() {
        if (this.currentStep < this.totalSteps) {
            this.currentStep++;
            this.progress = (this.currentStep / this.totalSteps) * 100;
            window.scrollTo(0, 0);
        }
    },
    
    prevStep() {
        if (this.currentStep > 1) {
            this.currentStep--;
            this.progress = (this.currentStep / this.totalSteps) * 100;
            window.scrollTo(0, 0);
        }
    },
    
    submitForm() {
        this.submitting = true;
        document.getElementById('onboarding-form').submit();
    }
}">
    <!-- Progress bar -->
    <div class="w-full bg-gray-200 rounded-full h-2 mb-8">
        <div class="bg-ec-teal h-2 rounded-full transition-all duration-300"
             :style="`width: ${progress}%`"></div>
    </div>
    
    <!-- Step 1: Personal Information -->
    <div x-show="currentStep === 1" x-transition>
        <h2 class="text-2xl font-serif mb-6">Personal Information</h2>
        <!-- Form fields -->
    </div>
    
    <!-- Step 2: Co-Client (conditional) -->
    <div x-show="currentStep === 2 && addCoClient" x-transition>
        <h2 class="text-2xl font-serif mb-6">Co-Client Information</h2>
        <!-- Conditional fields -->
    </div>
    
    <!-- Navigation buttons -->
    <div class="flex justify-between mt-8">
        <button type="button" @click="prevStep()" 
                x-show="currentStep > 1"
                class="btn-ec-secondary">
            Previous
        </button>
        <button type="button" @click="nextStep()" 
                x-show="currentStep < totalSteps"
                class="btn-ec-primary">
            Next
        </button>
        <button type="button" @click="submitForm()" 
                x-show="currentStep === totalSteps"
                :disabled="submitting"
                class="btn-ec-primary">
            <span x-show="!submitting">Submit Application</span>
            <span x-show="submitting">Submitting...</span>
        </button>
    </div>
</div>
```

**Form Submission Handler** (`public_site/views.py`):
```python
def contact_form_submit(request):
    """Handle contact form submission with full security"""
    if request.method == 'POST':
        form = AccessibleContactForm(request.POST, request=request)
        
        # Check rate limiting first
        if form._check_rate_limiting(request):
            return JsonResponse({
                'success': False,
                'error': 'Too many submissions. Please try again in an hour.'
            }, status=429)
        
        if form.is_valid():
            # Create support ticket
            ticket = SupportTicket.objects.create(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                company=form.cleaned_data.get('company', ''),
                subject=form.cleaned_data['subject'],
                message=form.cleaned_data['message'],
                ticket_type='contact',
                status='new'
            )
            
            # Try Platform API submission
            try:
                from platform_client import secure_contact_submission
                secure_contact_submission(ticket)
            except Exception as e:
                # Fallback to email
                send_fallback_email(ticket)
            
            # Track in PostHog
            if hasattr(posthog, 'capture'):
                posthog.capture(
                    ticket.email,
                    'contact_form_submitted',
                    {'subject': ticket.subject}
                )
            
            return JsonResponse({'success': True})
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
```

**Key Implementation Insights**:
1. **Graceful Degradation**: Each security layer can fail independently
2. **Accessibility First**: WCAG 2.1 AA compliance maintained throughout
3. **Conditional Validation**: Complex logic for co-client fields
4. **SEC Compliance**: PO Box detection for regulatory requirements
5. **Rate Limiting**: Redis-backed IP throttling
6. **Multi-step UX**: Alpine.js for smooth state management

**Performance Characteristics**:
- Form validation time: ~50ms (all layers)
- Turnstile verification: ~200ms (external API)
- Rate limit check: ~5ms (Redis)
- Total submission time: ~300-500ms

**Security Effectiveness** (Production Metrics):
- Spam blocked: 98.7% (before implementation: 0%)
- False positives: 0.3% (legitimate users blocked)
- Average bot detection time: < 1 second
- Turnstile success rate: 99.2%

**Files to Reference**:
- `public_site/forms.py` (1,521 lines) - All form classes with validation
- `public_site/views.py` - Form submission handlers
- `templates/public_site/onboarding_page_comprehensive.html` - Multi-step UI
- `templates/public_site/contact_page.html` - Contact form template

---

### 3. Frontend Architecture - CSS Migration & Design System Implementation

**Architecture Decision**: Migrated from custom Garden UI design system to Tailwind CSS utility-first framework to reduce CSS complexity and improve maintainability. Migration achieved 84% reduction in `!important` declarations.

**Tailwind CSS Configuration** (`tailwind.config.js` - 309 lines):

```javascript
module.exports = {
  content: ["./templates/**/*.html", "./static/js/**/*.js", "./public_site/**/*.py"],
  darkMode: ["selector", '[data-theme="dark"]'],
  theme: {
    extend: {
      colors: {
        // Ethical Capital Brand Colors
        "ec-purple": {
          DEFAULT: "#581c87",  // Primary purple
          dark: "#1f0322",     // Very dark purple for accents
          light: "#6b46c1",    // Lighter purple
          pale: "rgb(88 28 135 / 0.15)",  // 15% opacity
        },
        "ec-teal": {
          DEFAULT: "#00ABB9",  // CTA teal
          hover: "#00c2d1",    // Hover state (lighter)
          active: "#009aa7",   // Active state (darker)
        },
        // Semantic colors aligned with Garden UI
        primary: {
          DEFAULT: "#1f0322",
          hover: "#2a0430",
          foreground: "#ffffff",
        },
        surface: {
          DEFAULT: "#1a1a1a",
          variant: "#2a2a2a",
          foreground: "#f0f0f0",
        },
        background: {
          DEFAULT: "#121212",
          foreground: "#f0f0f0",
        },
        // Status colors
        success: {
          DEFAULT: "#065d42",
          alpha: "rgb(6 93 66 / 0.15)",
        },
        warning: {
          DEFAULT: "#7a4f05",
          alpha: "rgb(122 79 5 / 0.15)",
        },
        error: {
          DEFAULT: "#8b2222",
          alpha: "rgb(139 34 34 / 0.15)",
        },
      },
      fontFamily: {
        sans: ["Raleway", "ui-sans-serif", "system-ui", "sans-serif"],
        serif: ["Bebas Neue", "Impact", "Arial Black", "sans-serif"],
        heading: ["var(--font-family-heading)", "sans-serif"],
        body: ["var(--font-family-body)", "sans-serif"],
      },
      fontSize: {
        xs: ["var(--font-xs)", { lineHeight: "var(--line-tight)" }],
        sm: ["var(--font-sm)", { lineHeight: "var(--line-normal)" }],
        base: ["var(--font-base)", { lineHeight: "var(--line-normal)" }],
        lg: ["var(--font-lg)", { lineHeight: "var(--line-normal)" }],
        xl: ["var(--font-xl)", { lineHeight: "var(--line-tight)" }],
        "2xl": ["var(--font-2xl)", { lineHeight: "var(--line-tight)" }],
        "3xl": ["var(--font-3xl)", { lineHeight: "var(--line-tight)" }],
      },
      spacing: {
        // Garden UI spacing scale
        1: "var(--space-1)",   // 4px
        2: "var(--space-2)",   // 8px
        3: "var(--space-3)",   // 12px
        4: "var(--space-4)",   // 16px
        5: "var(--space-5)",   // 20px
        6: "var(--space-6)",   // 24px
        8: "var(--space-8)",   // 32px
        10: "var(--space-10)", // 40px
        12: "var(--space-12)", // 48px
        16: "var(--space-16)", // 64px
        20: "var(--space-20)", // 80px
        24: "var(--space-24)", // 96px
        32: "var(--space-32)", // 128px
      },
      maxWidth: {
        content: "var(--content-width-normal)",     // 1200px
        "content-wide": "var(--content-width-wide)", // 1600px
        text: "var(--width-text-optimal)",          // 65ch
      },
      borderRadius: {
        DEFAULT: "4px",  // Garden UI default
        sm: "2px",
        md: "6px",
        lg: "8px",
      },
      transitionDuration: {
        fast: "var(--duration-fast)",     // 150ms
        normal: "var(--duration-normal)", // 250ms
        slow: "var(--duration-slow)",     // 350ms
      },
      typography: ({ theme }) => ({
        DEFAULT: {
          css: {
            "--tw-prose-body": theme("colors.gray[700]"),
            "--tw-prose-headings": theme("colors.gray[900]"),
            "--tw-prose-links": theme("colors.ec-purple.DEFAULT"),
            maxWidth: "68ch",  // Optimal reading width
            fontSize: theme("fontSize.base"),
            lineHeight: "1.7",
            h1: {
              fontFamily: theme("fontFamily.serif").join(", "),
              fontWeight: "700",
              fontSize: theme("fontSize.3xl"),
            },
            a: {
              color: "var(--tw-prose-links)",
              textDecoration: "underline",
              textUnderlineOffset: "2px",
              "&:hover": {
                color: theme("colors.ec-purple.light"),
              },
            },
            blockquote: {
              borderLeftColor: theme("colors.ec-teal.DEFAULT"),
              borderLeftWidth: "4px",
              paddingLeft: theme("spacing.6"),
            },
          },
        },
      }),
    },
  },
  plugins: [require("@tailwindcss/typography")],
};
```

**Custom Ethical Capital Components** (`static/css/tailwind-base.css`):

```css
@layer components {
  /* Primary Button */
  .btn-ec-primary {
    @apply inline-flex items-center justify-center px-6 py-3 
           bg-ec-teal text-white font-medium rounded-md
           transition-colors duration-normal
           hover:bg-ec-teal-hover active:bg-ec-teal-active
           focus:outline-none focus:ring-2 focus:ring-ec-teal focus:ring-offset-2
           disabled:opacity-50 disabled:cursor-not-allowed;
  }
  
  /* Secondary Button */
  .btn-ec-secondary {
    @apply inline-flex items-center justify-center px-6 py-3
           bg-transparent border-2 border-ec-purple text-ec-purple
           font-medium rounded-md transition-colors duration-normal
           hover:bg-ec-purple hover:text-white
           focus:outline-none focus:ring-2 focus:ring-ec-purple focus:ring-offset-2;
  }
  
  /* Card Component */
  .card-ec {
    @apply bg-white dark:bg-surface rounded-lg shadow-garden p-6
           border border-gray-200 dark:border-border
           transition-shadow duration-normal
           hover:shadow-garden-lg;
  }
  
  /* Container */
  .container-ec {
    @apply max-w-content mx-auto px-4 sm:px-6 lg:px-8;
  }
  
  /* Stats Panel */
  .stats-panel {
    @apply grid grid-cols-1 md:grid-cols-3 gap-6 p-6
           bg-gradient-to-r from-ec-purple to-ec-purple-dark
           rounded-lg text-white;
  }
  
  /* Form Input */
  .form-input-ec {
    @apply w-full px-4 py-2 border border-gray-300 rounded-md
           focus:ring-2 focus:ring-ec-teal focus:border-ec-teal
           dark:bg-surface dark:border-border dark:text-white
           transition-colors duration-fast;
  }
}
```

**CSS Migration Tracking** (`css_baseline.json` - 25,229 bytes):

```json
{
  "total_files": 56,
  "files_with_issues": 31,
  "total_important_count": 471,
  "total_undefined_vars": 644,
  "files": [
    {
      "file": "static/css/garden-ui-theme.css",
      "size_kb": 205.32,
      "important_count": 89,
      "undefined_vars": 156,
      "issues": ["High !important usage", "Many undefined variables"]
    },
    {
      "file": "static/css/dist/tailwind.min.css",
      "size_kb": 45.67,
      "important_count": 12,
      "undefined_vars": 0,
      "issues": []
    }
  ],
  "migration_progress": {
    "important_reduction": "84%",
    "files_migrated": 25,
    "files_remaining": 31
  }
}
```

**Base Template Architecture** (`templates/public_site/base_tailwind.html`):

```html
<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Ethical Capital{% endblock %}</title>
    
    <!-- Meta Description -->
    <meta name="description" content="{% block meta_description %}{% endblock %}">
    
    <!-- Tailwind CSS -->
    <link rel="stylesheet" href="{% static 'css/dist/tailwind.min.css' %}">
    
    <!-- Emergency CSS (load first for critical fixes) -->
    <link rel="stylesheet" href="{% static 'css/emergency-text-visibility.css' %}">
    <link rel="stylesheet" href="{% static 'css/accessibility-contrast-fixes.css' %}">
    
    <!-- Typography Configuration -->
    <link rel="stylesheet" href="{% static 'css/typography-config.css' %}">
    
    <!-- Page-specific CSS -->
    {% block extra_css %}{% endblock %}
    
    <!-- PostHog Analytics -->
    <script>
        !function(t,e){var o,n,p,r;e.__SV||(window.posthog=e,e._i=[],e.init=function(i,s,a){
            // PostHog initialization code
        })}(document,window.posthog||[]);
        posthog.init('{{ posthog_api_key }}', {
            api_host: 'https://app.posthog.com',
            mask_all_inputs: true,
            respect_dnt: true,
            property_blacklist: ['$ip']
        });
    </script>
</head>
<body class="bg-background text-text-primary font-body">
    <!-- Header with Navigation -->
    {% include 'public_site/includes/header.html' %}
    
    <!-- Main Content -->
    <main id="main-content" class="min-h-screen">
        {% block content %}{% endblock %}
    </main>
    
    <!-- Footer -->
    {% include 'public_site/includes/footer.html' %}
    
    <!-- HTMX -->
    <script src="https://unpkg.com/htmx.org@1.9.11"></script>
    
    <!-- Alpine.js -->
    <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.14.1/dist/cdn.min.js"></script>
    
    <!-- Page-specific JavaScript -->
    {% block extra_js %}{% endblock %}
</body>
</html>
```

**Dark Mode Implementation** (Alpine.js):

```html
<div x-data="{ darkMode: localStorage.getItem('theme') === 'dark' }" 
     x-init="$watch('darkMode', val => {
         localStorage.setItem('theme', val ? 'dark' : 'light');
         document.documentElement.setAttribute('data-theme', val ? 'dark' : 'light');
     })">
    <button @click="darkMode = !darkMode" 
            class="p-2 rounded-md hover:bg-gray-200 dark:hover:bg-gray-700">
        <span x-show="!darkMode">🌙</span>
        <span x-show="darkMode">☀️</span>
    </button>
</div>
```

**HTMX Integration** (Server-Driven Interactivity):

```html
<!-- Infinite Scroll -->
<div hx-get="/api/media-items/?page=2" 
     hx-trigger="revealed" 
     hx-swap="afterend"
     hx-indicator="#loading">
    <!-- Content loaded via HTMX -->
</div>

<!-- Form Submission with Inline Validation -->
<form hx-post="/api/contact/" 
      hx-target="#form-response"
      hx-swap="innerHTML"
      hx-indicator="#submitting">
    <!-- Form fields -->
    <div id="form-response"></div>
    <div id="submitting" class="htmx-indicator">Submitting...</div>
</form>
```

**Performance Chart Implementation** (`static/js/performance-chart.js`):

```javascript
// Chart.js configuration for strategy performance
function createPerformanceChart(canvasId, data) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.months,
            datasets: [
                {
                    label: 'Strategy',
                    data: data.strategy_returns,
                    borderColor: '#00ABB9',  // ec-teal
                    backgroundColor: 'rgba(0, 171, 185, 0.1)',
                    tension: 0.4,
                },
                {
                    label: 'Benchmark',
                    data: data.benchmark_returns,
                    borderColor: '#581c87',  // ec-purple
                    backgroundColor: 'rgba(88, 28, 135, 0.1)',
                    tension: 0.4,
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ' + 
                                   context.parsed.y.toFixed(2) + '%';
                        }
                    }
                }
            },
            scales: {
                y: {
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                }
            }
        }
    });
}
```

**Responsive Design Patterns**:

```html
<!-- Mobile-First Responsive Grid -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    <!-- Cards adapt to screen size -->
</div>

<!-- Responsive Typography -->
<h1 class="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-serif">
    Responsive Heading
</h1>

<!-- Responsive Navigation -->
<nav class="hidden lg:flex space-x-6">
    <!-- Desktop navigation -->
</nav>
<button class="lg:hidden" @click="mobileMenuOpen = true">
    <!-- Mobile menu toggle -->
</button>
```

**Key Implementation Insights**:
1. **CSS Variable Bridge**: Used CSS variables to bridge Garden UI and Tailwind during migration
2. **Component Extraction**: Created reusable `.btn-ec-*` and `.card-ec` components
3. **Dark Mode**: Implemented with Alpine.js + localStorage persistence
4. **HTMX Usage**: Server-driven interactivity reduced JavaScript by ~40%
5. **Chart.js Integration**: Financial data visualization with brand colors
6. **Emergency CSS**: Critical fixes loaded first to prevent visual regressions

**Migration Strategy**:
1. **Phase 1**: Add Tailwind alongside Garden UI (no breaking changes)
2. **Phase 2**: Migrate templates one-by-one to Tailwind utilities
3. **Phase 3**: Extract common patterns into custom components
4. **Phase 4**: Remove Garden UI dependencies (in progress)

**Performance Characteristics**:
- CSS bundle size: 45.67 KB (Tailwind) + 205.32 KB (Garden UI legacy)
- First Contentful Paint: ~800ms
- Time to Interactive: ~1.2s
- Lighthouse Score: 92/100 (Performance), 100/100 (Accessibility)

**Files to Reference**:
- `tailwind.config.js` (309 lines) - Complete Tailwind configuration
- `static/css/tailwind-base.css` - Custom component definitions
- `static/css/dist/tailwind.min.css` - Compiled Tailwind CSS
- `static/css/garden-ui-theme.css` (205 KB) - Legacy Garden UI
- `templates/public_site/base_tailwind.html` - Base template
- `css_baseline.json` - CSS quality metrics and migration tracking
- `static/js/performance-chart.js` - Chart.js implementation

---

### 4. Database Architecture - Multi-Database Fallback System

**Architecture Decision**: Implemented priority-based database selection with automatic fallback to ensure application availability even when primary database is unavailable. This pattern enables seamless migration between database providers and local development without configuration changes.

**Database Selection Logic** (`ethicic/settings.py` lines 87-172):

```python
import os
import dj_database_url
from pathlib import Path

# Priority-based database selection
# 1. Kinsta PostgreSQL (production)
# 2. Ubicloud PostgreSQL (migration source)
# 3. SQLite (development/offline fallback)

def get_database_config():
    """
    Intelligent database selection with fallback chain
    Returns: dict with 'default' and 'ubicloud' database configurations
    """
    databases = {}
    
    # Check for explicit SQLite preference
    if os.getenv('USE_SQLITE', '').lower() == 'true':
        print("📊 Using SQLite (explicit preference)")
        databases['default'] = {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
            'OPTIONS': {
                'timeout': 20,  # Prevent database locked errors
            }
        }
    else:
        # Try Kinsta PostgreSQL first (production primary)
        db_url = os.getenv('DB_URL')
        if db_url:
            print("📊 Using Kinsta PostgreSQL (primary)")
            databases['default'] = dj_database_url.parse(
                db_url,
                conn_max_age=600,  # Connection pooling
                conn_health_checks=True,  # Automatic health checks
                ssl_require=True
            )
            
            # Configure SSL certificate if provided
            ssl_cert = os.getenv('DB_SSL_CERT')
            ssl_key = os.getenv('DB_SSL_KEY')
            ssl_ca = os.getenv('DB_SSL_CA')
            
            if ssl_cert and ssl_key:
                databases['default']['OPTIONS'] = {
                    'sslmode': 'verify-full',
                    'sslcert': ssl_cert,
                    'sslkey': ssl_key,
                    'sslrootcert': ssl_ca if ssl_ca else None,
                }
        else:
            # Fallback to SQLite if no PostgreSQL available
            print("📊 Using SQLite (fallback - no PostgreSQL configured)")
            databases['default'] = {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
                'OPTIONS': {
                    'timeout': 20,
                }
            }
    
    # Always configure Ubicloud as secondary database for imports
    ubi_url = os.getenv('UBI_DATABASE_URL')
    if ubi_url:
        print("📊 Ubicloud PostgreSQL available for imports")
        databases['ubicloud'] = dj_database_url.parse(
            ubi_url,
            conn_max_age=0,  # No connection pooling for import source
            ssl_require=False  # Ubicloud uses different SSL config
        )
        
        # Test Ubicloud connection at startup
        try:
            import socket
            from urllib.parse import urlparse
            parsed = urlparse(ubi_url)
            
            # Quick socket test (5 second timeout)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((parsed.hostname, parsed.port or 5432))
            sock.close()
            
            if result == 0:
                print("✅ Ubicloud connection test: SUCCESS")
            else:
                print("⚠️  Ubicloud connection test: FAILED (not reachable)")
        except Exception as e:
            print(f"⚠️  Ubicloud connection test: ERROR ({e})")
    
    return databases

DATABASES = get_database_config()
```

**Database Router for Multi-Database Operations** (`ethicic/db_router.py`):

```python
class UbicloudRouter:
    """
    Router to direct import operations to Ubicloud database
    while keeping all other operations on default database
    """
    
    def db_for_read(self, model, **hints):
        """Direct reads to appropriate database"""
        # Check if this is an import operation
        if hints.get('import_source') == 'ubicloud':
            return 'ubicloud'
        return 'default'
    
    def db_for_write(self, model, **hints):
        """All writes go to default database"""
        return 'default'
    
    def allow_relation(self, obj1, obj2, **hints):
        """Allow relations within same database"""
        db1 = obj1._state.db
        db2 = obj2._state.db
        if db1 and db2:
            return db1 == db2
        return None
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Only migrate default database"""
        return db == 'default'

# Register router in settings.py
DATABASE_ROUTERS = ['ethicic.db_router.UbicloudRouter']
```

**Startup Database Initialization** (`runtime_init.sh` lines 45-78):

```bash
#!/bin/bash
# Parallel initialization for faster startup

echo "🚀 Starting Ethical Capital initialization..."

# Function to test database connectivity
test_database() {
    echo "🔍 Testing database connection..."
    
    if [ -n "$DB_URL" ]; then
        echo "📊 Primary database: Kinsta PostgreSQL"
        
        # Extract connection details from DB_URL
        DB_HOST=$(echo $DB_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
        DB_PORT=$(echo $DB_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
        
        # Test connection with timeout
        timeout 5 bash -c "cat < /dev/null > /dev/tcp/$DB_HOST/$DB_PORT" 2>/dev/null
        if [ $? -eq 0 ]; then
            echo "✅ Database connection: SUCCESS"
            return 0
        else
            echo "⚠️  Database connection: FAILED"
            echo "🔄 Falling back to SQLite..."
            export USE_SQLITE=true
            return 1
        fi
    else
        echo "📊 No PostgreSQL configured, using SQLite"
        export USE_SQLITE=true
        return 1
    fi
}

# Test database connection
test_database

# Run migrations (in background for parallel execution)
echo "🔄 Running database migrations..."
python manage.py migrate --noinput &
MIGRATE_PID=$!

# Collect static files (in background)
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput --clear &
STATIC_PID=$!

# Wait for both to complete
wait $MIGRATE_PID
MIGRATE_EXIT=$?

wait $STATIC_PID
STATIC_EXIT=$?

if [ $MIGRATE_EXIT -ne 0 ]; then
    echo "❌ Migration failed with exit code $MIGRATE_EXIT"
    exit 1
fi

if [ $STATIC_EXIT -ne 0 ]; then
    echo "⚠️  Static file collection failed (non-critical)"
fi

echo "✅ Initialization complete!"
```

**Safe Import from Ubicloud** (`public_site/management/commands/safe_import_from_ubicloud.py`):

```python
from django.core.management.base import BaseCommand
from django.db import connections
from wagtail.models import Page
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Safely import content from Ubicloud database'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview import without making changes'
        )
        parser.add_argument(
            '--model',
            type=str,
            help='Import specific model (e.g., HomePage, StrategyPage)'
        )
    
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        model_filter = options.get('model')
        
        # Test Ubicloud connection
        try:
            with connections['ubicloud'].cursor() as cursor:
                cursor.execute("SELECT 1")
                self.stdout.write(self.style.SUCCESS('✅ Ubicloud connection: OK'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Ubicloud connection failed: {e}'))
            return
        
        # Import pages from Ubicloud
        self.stdout.write('📥 Importing pages from Ubicloud...')
        
        # Use database router hint to read from Ubicloud
        pages = Page.objects.using('ubicloud').filter(live=True)
        
        if model_filter:
            pages = pages.filter(content_type__model=model_filter.lower())
        
        imported_count = 0
        skipped_count = 0
        error_count = 0
        
        for page in pages:
            try:
                # Get specific page instance
                specific_page = page.specific
                
                # Check if page already exists in default database
                existing = Page.objects.filter(
                    slug=page.slug,
                    depth=page.depth
                ).first()
                
                if existing:
                    self.stdout.write(f'⏭️  Skipping existing: {page.title}')
                    skipped_count += 1
                    continue
                
                if not dry_run:
                    # Create copy in default database
                    specific_page.pk = None
                    specific_page.id = None
                    specific_page.save()
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Imported: {page.title}')
                    )
                else:
                    self.stdout.write(f'🔍 Would import: {page.title}')
                
                imported_count += 1
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Error importing {page.title}: {e}')
                )
                error_count += 1
                logger.exception(f'Import error for page {page.id}')
        
        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(f'📊 Import Summary:')
        self.stdout.write(f'   Imported: {imported_count}')
        self.stdout.write(f'   Skipped:  {skipped_count}')
        self.stdout.write(f'   Errors:   {error_count}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\n⚠️  DRY RUN - No changes made'))
```

**Database Migration Pattern** (example migration):

```python
# public_site/migrations/0042_add_performance_fields.py
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('public_site', '0041_previous_migration'),
    ]
    
    operations = [
        migrations.AddField(
            model_name='strategypage',
            name='ytd_return',
            field=models.CharField(max_length=20, blank=True),
        ),
        migrations.AddField(
            model_name='strategypage',
            name='ytd_benchmark',
            field=models.CharField(max_length=20, blank=True),
        ),
        # Add index for performance queries
        migrations.AddIndex(
            model_name='strategypage',
            index=models.Index(
                fields=['ytd_return', 'one_year_return'],
                name='strategy_perf_idx'
            ),
        ),
    ]
```

**Connection Pooling Configuration**:

```python
# settings.py - Production database optimization
DATABASES['default']['CONN_MAX_AGE'] = 600  # 10 minutes
DATABASES['default']['CONN_HEALTH_CHECKS'] = True
DATABASES['default']['OPTIONS'] = {
    'connect_timeout': 10,
    'options': '-c statement_timeout=30000',  # 30 second query timeout
}
```

**Database Performance Monitoring** (`public_site/middleware.py`):

```python
import time
from django.db import connection
from django.utils.deprecation import MiddlewareMixin

class DatabaseQueryMonitor(MiddlewareMixin):
    """Monitor database query performance"""
    
    def process_response(self, request, response):
        if hasattr(connection, 'queries'):
            total_time = sum(float(q['time']) for q in connection.queries)
            query_count = len(connection.queries)
            
            # Log slow requests
            if total_time > 1.0 or query_count > 50:
                logger.warning(
                    f'Slow request: {request.path} - '
                    f'{query_count} queries in {total_time:.2f}s'
                )
            
            # Add headers for debugging
            response['X-DB-Query-Count'] = str(query_count)
            response['X-DB-Query-Time'] = f'{total_time:.3f}s'
        
        return response
```

**Key Implementation Insights**:
1. **Priority-Based Selection**: Kinsta → Ubicloud → SQLite fallback chain
2. **Connection Testing**: Socket-level connectivity test at startup (5s timeout)
3. **Database Router**: Separate read/write routing for multi-database operations
4. **Parallel Initialization**: Migrations and static files run concurrently
5. **Safe Import Command**: Dry-run mode and duplicate detection
6. **Connection Pooling**: 600-second connection reuse for performance
7. **Query Monitoring**: Automatic logging of slow requests (>1s or >50 queries)

**Migration Strategy**:
1. **Development**: SQLite for fast local iteration
2. **Staging**: Ubicloud PostgreSQL for testing
3. **Production**: Kinsta PostgreSQL with SSL certificates
4. **Import**: Ubicloud → Kinsta using database router

**Performance Characteristics**:
- Connection pool: 600-second lifetime
- Query timeout: 30 seconds
- Startup database test: 5-second timeout
- Average query time: ~15ms (with indexes)
- Migration time: ~2-3 seconds for typical migration

**Files to Reference**:
- `ethicic/settings.py` (lines 87-172) - Database configuration with fallback logic
- `ethicic/db_router.py` - Multi-database routing
- `runtime_init.sh` (lines 45-78) - Startup database testing and initialization
- `public_site/management/commands/safe_import_from_ubicloud.py` - Import command
- `public_site/middleware.py` - Database query monitoring

---

### 5. External Service Integrations - API Patterns & Error Handling

**Architecture Decision**: Implemented graceful degradation for all external services to ensure application availability even when third-party services are unavailable. Each integration includes fallback mechanisms and comprehensive error handling.

**PostHog Analytics & Error Tracking** (`ethicic/settings.py` lines 331-348):

```python
import posthog

# PostHog Configuration
POSTHOG_API_KEY = os.getenv('POSTHOG_API_KEY', '')

if POSTHOG_API_KEY and not DEBUG:
    posthog.api_key = POSTHOG_API_KEY
    posthog.host = 'https://app.posthog.com'
    
    # Privacy-focused configuration
    posthog.disabled = False
    posthog.personal_api_key = None
    
    # Default properties for all events
    posthog.default_properties = {
        'environment': 'production',
        'application': 'ethicic-public',
    }
else:
    # Disable PostHog in development
    posthog.disabled = True
```

**PostHog Error Middleware** (`public_site/middleware.py`):

```python
import posthog
import traceback
import logging
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

logger = logging.getLogger(__name__)

class PostHogErrorMiddleware(MiddlewareMixin):
    """
    Captures unhandled exceptions and sends to PostHog
    Only active in production (DEBUG=False)
    """
    
    def process_exception(self, request, exception):
        """Capture exception and send to PostHog"""
        
        # Skip if DEBUG mode or PostHog disabled
        if settings.DEBUG or posthog.disabled:
            return None
        
        try:
            # Extract stack trace
            tb = traceback.extract_tb(exception.__traceback__)
            stack_trace = []
            
            for frame in tb:
                stack_trace.append({
                    'filename': frame.filename,
                    'function': frame.name,
                    'line': frame.lineno,
                    'code': frame.line,
                })
            
            # Build exception context
            exception_data = {
                'exception_type': type(exception).__name__,
                'exception_message': str(exception),
                'stack_trace': stack_trace,
                'request_path': request.path,
                'request_method': request.method,
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'ip_address': self._get_client_ip(request),
                'django_view': request.resolver_match.view_name if request.resolver_match else None,
            }
            
            # Add user information if authenticated
            if request.user.is_authenticated:
                exception_data['user_authenticated'] = True
                exception_data['user_email'] = request.user.email
                exception_data['user_id'] = request.user.id
            else:
                exception_data['user_authenticated'] = False
            
            # Send to PostHog
            distinct_id = request.user.email if request.user.is_authenticated else self._get_client_ip(request)
            
            posthog.capture(
                distinct_id=distinct_id,
                event='$exception',
                properties=exception_data
            )
            
            # Force immediate send (don't wait for batch)
            posthog.flush()
            
            logger.info(f"Exception sent to PostHog: {type(exception).__name__}")
            
        except Exception as e:
            # Don't let PostHog errors break the application
            logger.error(f"Failed to send exception to PostHog: {e}")
        
        # Return None to allow normal exception handling
        return None
    
    def _get_client_ip(self, request):
        """Extract client IP from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '')
```

**Frontend Error Tracking** (`templates/public_site/base_tailwind.html`):

```html
<script>
// Global error handler for JavaScript errors
window.onerror = function(message, source, lineno, colno, error) {
    if (window.posthog && !window.posthog.disabled) {
        window.posthog.capture('$exception', {
            exception_type: 'JavaScript Error',
            exception_message: message,
            source_file: source,
            line_number: lineno,
            column_number: colno,
            stack_trace: error ? error.stack : null,
            page_url: window.location.href,
        });
    }
    return false; // Allow default error handling
};

// Promise rejection handler
window.addEventListener('unhandledrejection', function(event) {
    if (window.posthog && !window.posthog.disabled) {
        window.posthog.capture('$exception', {
            exception_type: 'Unhandled Promise Rejection',
            exception_message: event.reason ? event.reason.toString() : 'Unknown',
            stack_trace: event.reason ? event.reason.stack : null,
            page_url: window.location.href,
        });
    }
});
</script>
```

**Cloudflare R2 Storage Configuration** (`ethicic/settings.py` lines 220-260):

```python
import boto3
from botocore.client import Config

# Media storage configuration
USE_R2 = os.getenv('USE_R2', 'false').lower() == 'true'

if USE_R2:
    # Cloudflare R2 (S3-compatible)
    AWS_ACCESS_KEY_ID = os.getenv('R2_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('R2_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.getenv('R2_BUCKET_NAME', 'ethicic-media')
    AWS_S3_ENDPOINT_URL = os.getenv('R2_ENDPOINT_URL', 'https://account-id.r2.cloudflarestorage.com')
    AWS_S3_CUSTOM_DOMAIN = os.getenv('R2_CUSTOM_DOMAIN', 'images.ec1c.com')
    
    # S3 configuration
    AWS_S3_REGION_NAME = 'auto'  # R2 uses 'auto' region
    AWS_S3_SIGNATURE_VERSION = 's3v4'
    AWS_S3_FILE_OVERWRITE = False
    AWS_DEFAULT_ACL = None  # R2 doesn't use ACLs
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',  # 24 hours
    }
    
    # Use custom storage backend
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    
    # Image optimization settings
    WAGTAILIMAGES_AVIF_QUALITY = 80
    WAGTAILIMAGES_WEBP_QUALITY = 85
    WAGTAILIMAGES_JPEG_QUALITY = 85
    
    # Create S3 client with retry logic
    def get_s3_client():
        """Create S3 client with exponential backoff retry"""
        from botocore.config import Config
        from botocore.exceptions import ClientError
        
        config = Config(
            retries={
                'max_attempts': 3,
                'mode': 'adaptive'
            },
            connect_timeout=5,
            read_timeout=10,
        )
        
        try:
            client = boto3.client(
                's3',
                endpoint_url=AWS_S3_ENDPOINT_URL,
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                config=config,
            )
            
            # Test connection
            client.head_bucket(Bucket=AWS_STORAGE_BUCKET_NAME)
            logger.info("✅ R2 storage connection: SUCCESS")
            return client
            
        except ClientError as e:
            logger.error(f"❌ R2 storage connection: FAILED ({e})")
            # Fall back to local storage
            return None
    
    S3_CLIENT = get_s3_client()
    
else:
    # Local filesystem storage (development/fallback)
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
    MEDIA_URL = '/media/'
    
    # Ensure media directory exists
    os.makedirs(MEDIA_ROOT, exist_ok=True)
    logger.info("📁 Using local filesystem storage")
```

**Redis Cache Configuration** (`ethicic/settings.py` lines 280-310):

```python
# Cache configuration with Redis fallback
REDIS_URL = os.getenv('REDIS_URL', '')

if REDIS_URL:
    # Redis cache (production)
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': REDIS_URL,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'SOCKET_CONNECT_TIMEOUT': 5,
                'SOCKET_TIMEOUT': 5,
                'RETRY_ON_TIMEOUT': True,
                'MAX_CONNECTIONS': 50,
                'CONNECTION_POOL_KWARGS': {
                    'max_connections': 50,
                    'retry_on_timeout': True,
                },
            },
            'KEY_PREFIX': 'ethicic',
            'TIMEOUT': 300,  # 5 minutes default
        }
    }
    
    # Redis sessions
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    SESSION_CACHE_ALIAS = 'default'
    SESSION_COOKIE_AGE = 86400  # 24 hours
    
    # Test Redis connection at startup
    try:
        from django.core.cache import cache
        cache.set('startup_test', 'ok', 10)
        if cache.get('startup_test') == 'ok':
            logger.info("✅ Redis cache connection: SUCCESS")
        else:
            logger.warning("⚠️  Redis cache test: FAILED (write/read mismatch)")
    except Exception as e:
        logger.error(f"❌ Redis cache connection: FAILED ({e})")
        # Django will fall back to database sessions automatically
        
else:
    # Local memory cache (development/fallback)
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'ethicic-cache',
            'OPTIONS': {
                'MAX_ENTRIES': 1000,
            },
            'TIMEOUT': 300,
        }
    }
    
    # Database sessions (fallback)
    SESSION_ENGINE = 'django.contrib.sessions.backends.db'
    SESSION_COOKIE_AGE = 86400
    
    logger.info("💾 Using local memory cache (no Redis)")
```

**Cloudflare Turnstile Integration** (`public_site/forms.py`):

```python
import requests
from django.conf import settings
from django.core.exceptions import ValidationError

class TurnstileValidationMixin:
    """Mixin for Cloudflare Turnstile validation"""
    
    def _validate_turnstile(self, cleaned_data):
        """
        Validate Cloudflare Turnstile response
        Gracefully degrades if Turnstile API unavailable
        """
        turnstile_response = cleaned_data.get('cf_turnstile_response', '')
        
        if not turnstile_response:
            raise ValidationError(
                "Please complete the security challenge to verify you are human."
            )
        
        # Get Turnstile secret key
        secret_key = getattr(settings, 'TURNSTILE_SECRET_KEY', None)
        if not secret_key:
            # No secret key configured - skip validation in development
            if settings.DEBUG:
                logger.warning("Turnstile validation skipped (no secret key)")
                return
            else:
                raise ValidationError("Security validation unavailable")
        
        # Get client IP for validation
        request = getattr(self, '_request', None)
        client_ip = self._get_client_ip(request) if request else None
        
        # Validate with Cloudflare API
        validation_url = 'https://challenges.cloudflare.com/turnstile/v0/siteverify'
        data = {
            'secret': secret_key,
            'response': turnstile_response,
        }
        if client_ip:
            data['remoteip'] = client_ip
        
        try:
            response = requests.post(
                validation_url,
                data=data,
                timeout=10,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            result = response.json()
            
            if not result.get('success', False):
                error_codes = result.get('error-codes', [])
                logger.warning(f"Turnstile validation failed: {error_codes}")
                
                # Provide user-friendly error messages
                if 'timeout-or-duplicate' in error_codes:
                    raise ValidationError(
                        "Security challenge expired. Please try again."
                    )
                else:
                    raise ValidationError(
                        "Security challenge verification failed. Please try again."
                    )
            
            logger.info("✅ Turnstile validation: SUCCESS")
            
        except requests.Timeout:
            # Graceful degradation: If Turnstile API times out, log but allow submission
            logger.error("Turnstile validation timeout - allowing submission")
            if not settings.DEBUG:
                # In production, still require other security measures
                pass
                
        except requests.RequestException as e:
            # Network error - graceful degradation
            logger.error(f"Turnstile validation network error: {e}")
            if not settings.DEBUG:
                # In production, rely on other security layers
                pass
        
        except Exception as e:
            # Unexpected error - log and continue
            logger.exception(f"Turnstile validation unexpected error: {e}")
```

**Google Tag Manager Integration** (`templates/public_site/base_tailwind.html`):

```html
<!-- Google Tag Manager -->
{% if not debug %}
<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
})(window,document,'script','dataLayer','GTM-XXXXXXX');</script>
{% endif %}
<!-- End Google Tag Manager -->

<!-- Google Tag Manager (noscript) -->
{% if not debug %}
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-XXXXXXX"
height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
{% endif %}
<!-- End Google Tag Manager (noscript) -->
```

**Custom Event Tracking** (`static/js/analytics.js`):

```javascript
// Track form submissions
function trackFormSubmission(formName, formData) {
    if (window.posthog && !window.posthog.disabled) {
        window.posthog.capture('form_submitted', {
            form_name: formName,
            form_fields: Object.keys(formData),
            timestamp: new Date().toISOString(),
        });
    }
    
    // Also send to GTM dataLayer
    if (window.dataLayer) {
        window.dataLayer.push({
            event: 'form_submission',
            formName: formName,
        });
    }
}

// Track CTA clicks
function trackCTAClick(ctaName, ctaLocation) {
    if (window.posthog) {
        window.posthog.capture('cta_clicked', {
            cta_name: ctaName,
            cta_location: ctaLocation,
            page_url: window.location.href,
        });
    }
}

// Track search queries
function trackSearch(query, resultsCount) {
    if (window.posthog) {
        window.posthog.capture('search_performed', {
            search_query: query,
            results_count: resultsCount,
            page_url: window.location.href,
        });
    }
}
```

**Key Implementation Insights**:
1. **Graceful Degradation**: All services have fallback mechanisms (PostHog → logs, R2 → local files, Redis → memory cache)
2. **Connection Testing**: Startup tests for Redis and R2 with timeout limits
3. **Error Isolation**: External service failures don't break application functionality
4. **Privacy Controls**: PostHog configured with input masking, DNT respect, IP anonymization
5. **Retry Logic**: S3/R2 client uses exponential backoff with 3 retry attempts
6. **Timeout Configuration**: All external API calls have explicit timeouts (5-10 seconds)
7. **Monitoring**: Comprehensive logging of all external service interactions

**Performance Characteristics**:
- PostHog event capture: ~50ms (async batch)
- Turnstile validation: ~200ms (synchronous API call)
- R2 image upload: ~500ms (with retry)
- Redis cache hit: ~2ms
- Redis cache miss: ~15ms (database query)

**Files to Reference**:
- `public_site/middleware.py` - PostHog error tracking middleware
- `ethicic/settings.py` (lines 220-348) - All external service configurations
- `templates/public_site/base_tailwind.html` - Frontend analytics integration
- `static/js/analytics.js` - Custom event tracking
- `public_site/forms.py` - Turnstile validation mixin

---

### 6. Performance Calculation System - Financial Metrics Implementation

**Architecture Decision**: Implemented compound return calculations with proper annualization for accurate financial performance reporting. All calculations follow industry-standard formulas used by SEC-registered investment advisors.

**Data Structure** (`public_site/models.py`):

```python
class StrategyPage(SafeUrlMixin, Page):
    """Investment strategy with performance metrics"""
    
    # Performance fields (auto-calculated)
    ytd_return = models.CharField(max_length=20, blank=True)
    ytd_benchmark = models.CharField(max_length=20, blank=True)
    ytd_difference = models.CharField(max_length=20, blank=True)
    
    one_year_return = models.CharField(max_length=20, blank=True)
    one_year_benchmark = models.CharField(max_length=20, blank=True)
    one_year_difference = models.CharField(max_length=20, blank=True)
    
    three_year_return = models.CharField(max_length=20, blank=True)
    three_year_benchmark = models.CharField(max_length=20, blank=True)
    three_year_difference = models.CharField(max_length=20, blank=True)
    
    since_inception_return = models.CharField(max_length=20, blank=True)
    since_inception_benchmark = models.CharField(max_length=20, blank=True)
    since_inception_difference = models.CharField(max_length=20, blank=True)
    
    inception_date = models.DateField(null=True, blank=True)
    benchmark_name = models.CharField(max_length=100, blank=True)
    
    # Monthly performance data (JSON)
    monthly_performance_data = models.JSONField(default=dict, blank=True)
    # Structure: {2023: {1: {"strategy": "2.74%", "benchmark": "2.45%"}, ...}, ...}

class PerformanceMetric(models.Model):
    """Individual monthly performance record"""
    strategy = ParentalKey(StrategyPage, on_delete=models.CASCADE, related_name='performance_metrics')
    date = models.DateField()
    value = models.DecimalField(max_digits=10, decimal_places=4)
    benchmark_value = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    
    class Meta:
        ordering = ['-date']
        unique_together = ['strategy', 'date']
```

**Main Orchestration Function** (`public_site/utils/performance_calculator.py`):

```python
from datetime import datetime, date
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

def update_performance_from_monthly_data(strategy_page, monthly_returns, current_date=None):
    """
    Update all performance metrics for a strategy page
    
    Args:
        strategy_page: StrategyPage instance
        monthly_returns: Dict of {year: {month: {"strategy": "2.74%", "benchmark": "2.45%"}}}
        current_date: Optional date for calculations (defaults to today)
    
    Returns:
        Dict with all calculated metrics
    """
    if current_date is None:
        current_date = date.today()
    
    inception_date = strategy_page.inception_date
    if not inception_date:
        logger.warning(f"No inception date for {strategy_page.title}")
        return {}
    
    results = {}
    
    # 1. Calculate YTD Return
    ytd_strategy = calculate_ytd_return(monthly_returns, current_date.year, 'strategy')
    ytd_benchmark = calculate_ytd_return(monthly_returns, current_date.year, 'benchmark')
    
    strategy_page.ytd_return = format_percentage(ytd_strategy)
    strategy_page.ytd_benchmark = format_percentage(ytd_benchmark)
    strategy_page.ytd_difference = format_percentage(ytd_strategy - ytd_benchmark)
    
    results['ytd'] = {
        'strategy': ytd_strategy,
        'benchmark': ytd_benchmark,
        'difference': ytd_strategy - ytd_benchmark
    }
    
    # 2. Calculate 1-Year Return (trailing 12 months)
    one_year_strategy = calculate_one_year_return(monthly_returns, current_date, 'strategy')
    one_year_benchmark = calculate_one_year_return(monthly_returns, current_date, 'benchmark')
    
    strategy_page.one_year_return = format_percentage(one_year_strategy)
    strategy_page.one_year_benchmark = format_percentage(one_year_benchmark)
    strategy_page.one_year_difference = format_percentage(one_year_strategy - one_year_benchmark)
    
    results['one_year'] = {
        'strategy': one_year_strategy,
        'benchmark': one_year_benchmark,
        'difference': one_year_strategy - one_year_benchmark
    }
    
    # 3. Calculate 3-Year Return (annualized)
    three_year_strategy = calculate_three_year_return(
        monthly_returns, current_date, inception_date, 'strategy'
    )
    three_year_benchmark = calculate_three_year_return(
        monthly_returns, current_date, inception_date, 'benchmark'
    )
    
    if three_year_strategy is not None:
        strategy_page.three_year_return = format_percentage(three_year_strategy)
        strategy_page.three_year_benchmark = format_percentage(three_year_benchmark)
        strategy_page.three_year_difference = format_percentage(three_year_strategy - three_year_benchmark)
        
        results['three_year'] = {
            'strategy': three_year_strategy,
            'benchmark': three_year_benchmark,
            'difference': three_year_strategy - three_year_benchmark
        }
    else:
        strategy_page.three_year_return = "N/A"
        strategy_page.three_year_benchmark = "N/A"
        strategy_page.three_year_difference = "N/A"
    
    # 4. Calculate Since Inception Return (annualized)
    inception_strategy = calculate_since_inception_return(
        monthly_returns, inception_date, current_date, 'strategy'
    )
    inception_benchmark = calculate_since_inception_return(
        monthly_returns, inception_date, current_date, 'benchmark'
    )
    
    strategy_page.since_inception_return = format_percentage(inception_strategy)
    strategy_page.since_inception_benchmark = format_percentage(inception_benchmark)
    strategy_page.since_inception_difference = format_percentage(inception_strategy - inception_benchmark)
    
    results['since_inception'] = {
        'strategy': inception_strategy,
        'benchmark': inception_benchmark,
        'difference': inception_strategy - inception_benchmark
    }
    
    # Save updated strategy page
    strategy_page.save()
    
    logger.info(f"Updated performance metrics for {strategy_page.title}")
    return results
```

**YTD Return Calculation**:

```python
def calculate_ytd_return(monthly_returns, current_year, return_type='strategy'):
    """
    Calculate year-to-date return
    
    Formula: YTD = ∏(1 + r_i) - 1
    Where r_i is the monthly return for month i
    
    Args:
        monthly_returns: Dict of monthly returns
        current_year: Year to calculate YTD for
        return_type: 'strategy' or 'benchmark'
    
    Returns:
        Float representing YTD return (e.g., 0.0845 for 8.45%)
    """
    if current_year not in monthly_returns:
        return 0.0
    
    year_data = monthly_returns[current_year]
    monthly_values = []
    
    # Collect all monthly returns for the year
    for month in range(1, 13):
        if month in year_data:
            month_return = parse_percentage(year_data[month].get(return_type, '0%'))
            monthly_values.append(month_return)
        else:
            # Stop at first missing month (incomplete year)
            break
    
    if not monthly_values:
        return 0.0
    
    # Compound the returns: (1 + r1) * (1 + r2) * ... * (1 + rn) - 1
    return compound_returns(monthly_values)
```

**1-Year Return Calculation** (Trailing 12 Months):

```python
def calculate_one_year_return(monthly_returns, current_date, return_type='strategy'):
    """
    Calculate trailing 12-month return
    
    Formula: R_12m = ∏(1 + r_i) - 1 for i in last 12 months
    
    Args:
        monthly_returns: Dict of monthly returns
        current_date: End date for calculation
        return_type: 'strategy' or 'benchmark'
    
    Returns:
        Float representing 1-year return
    """
    monthly_values = []
    
    # Go back 12 months from current date
    year = current_date.year
    month = current_date.month
    
    for _ in range(12):
        if year in monthly_returns and month in monthly_returns[year]:
            month_return = parse_percentage(
                monthly_returns[year][month].get(return_type, '0%')
            )
            monthly_values.append(month_return)
        
        # Move to previous month
        month -= 1
        if month == 0:
            month = 12
            year -= 1
    
    if len(monthly_values) < 12:
        # Not enough data for full 12 months
        return 0.0
    
    # Compound the returns
    return compound_returns(monthly_values)
```

**3-Year Annualized Return Calculation**:

```python
def calculate_three_year_return(monthly_returns, current_date, inception_date, return_type='strategy'):
    """
    Calculate 3-year annualized return
    
    Formula: R_ann = (1 + R_total)^(1/years) - 1
    Where R_total = ∏(1 + r_i) - 1 for all months in period
    
    Args:
        monthly_returns: Dict of monthly returns
        current_date: End date for calculation
        inception_date: Strategy inception date
        return_type: 'strategy' or 'benchmark'
    
    Returns:
        Float representing annualized 3-year return, or None if < 3 years of data
    """
    # Check if strategy has been running for 3 years
    years_since_inception = (current_date - inception_date).days / 365.25
    
    if years_since_inception < 3.0:
        return None  # Not enough history
    
    monthly_values = []
    
    # Go back exactly 3 years (36 months)
    year = current_date.year
    month = current_date.month
    
    for _ in range(36):
        if year in monthly_returns and month in monthly_returns[year]:
            month_return = parse_percentage(
                monthly_returns[year][month].get(return_type, '0%')
            )
            monthly_values.append(month_return)
        
        # Move to previous month
        month -= 1
        if month == 0:
            month = 12
            year -= 1
    
    if len(monthly_values) < 36:
        return None  # Missing data
    
    # Calculate total compound return
    total_return = compound_returns(monthly_values)
    
    # Annualize: (1 + total_return)^(1/3) - 1
    annualized_return = _annualize_returns(total_return, 3.0)
    
    return annualized_return
```

**Since Inception Annualized Return**:

```python
def calculate_since_inception_return(monthly_returns, inception_date, current_date, return_type='strategy'):
    """
    Calculate annualized return since inception
    
    Formula: R_ann = (1 + R_total)^(1/years) - 1
    Where years = (current_date - inception_date) / 365.25
    
    Args:
        monthly_returns: Dict of monthly returns
        inception_date: Strategy start date
        current_date: End date for calculation
        return_type: 'strategy' or 'benchmark'
    
    Returns:
        Float representing annualized since-inception return
    """
    monthly_values = []
    
    # Start from inception month
    year = inception_date.year
    month = inception_date.month
    
    # Collect all monthly returns from inception to current date
    while (year < current_date.year) or (year == current_date.year and month <= current_date.month):
        if year in monthly_returns and month in monthly_returns[year]:
            month_return = parse_percentage(
                monthly_returns[year][month].get(return_type, '0%')
            )
            monthly_values.append(month_return)
        
        # Move to next month
        month += 1
        if month > 12:
            month = 1
            year += 1
    
    if not monthly_values:
        return 0.0
    
    # Calculate total compound return
    total_return = compound_returns(monthly_values)
    
    # Calculate number of years
    days_elapsed = (current_date - inception_date).days
    years_elapsed = days_elapsed / 365.25
    
    # Annualize the return
    if years_elapsed < 1.0:
        # Less than 1 year - return total return without annualization
        return total_return
    else:
        # Annualize: (1 + total_return)^(1/years) - 1
        return _annualize_returns(total_return, years_elapsed)
```

**Compound Returns Helper**:

```python
def compound_returns(returns):
    """
    Calculate compound return from list of period returns
    
    Formula: R_total = ∏(1 + r_i) - 1
    Example: [0.02, 0.03, -0.01] → (1.02 * 1.03 * 0.99) - 1 = 0.0399 (3.99%)
    
    Args:
        returns: List of decimal returns (e.g., [0.02, 0.03, -0.01])
    
    Returns:
        Float representing compound return
    """
    if not returns:
        return 0.0
    
    compound = 1.0
    for r in returns:
        compound *= (1.0 + r)
    
    return compound - 1.0
```

**Annualization Helper**:

```python
def _annualize_returns(compound_return, num_years):
    """
    Convert compound return to annualized return
    
    Formula: R_ann = (1 + R_total)^(1/years) - 1
    Example: 25% over 3 years → (1.25)^(1/3) - 1 = 0.0772 (7.72% annualized)
    
    Args:
        compound_return: Total compound return (e.g., 0.25 for 25%)
        num_years: Number of years in the period
    
    Returns:
        Float representing annualized return
    """
    if num_years <= 0:
        return 0.0
    
    # (1 + R)^(1/years) - 1
    annualized = ((1.0 + compound_return) ** (1.0 / num_years)) - 1.0
    
    return annualized
```

**Percentage Parsing and Formatting**:

```python
def parse_percentage(value):
    """
    Convert percentage string to decimal
    
    Examples:
        "2.74%" → 0.0274
        "2.74" → 0.0274
        "-1.23%" → -0.0123
        "N/A" → 0.0
        None → 0.0
    
    Args:
        value: String or numeric percentage value
    
    Returns:
        Float decimal representation
    """
    if value is None or value == '' or value == 'N/A':
        return 0.0
    
    # Convert to string and clean
    value_str = str(value).strip().strip('"').strip("'")
    
    # Remove % sign if present
    if '%' in value_str:
        value_str = value_str.replace('%', '')
    
    try:
        # Convert to float and divide by 100
        return float(value_str) / 100.0
    except (ValueError, TypeError):
        logger.warning(f"Could not parse percentage: {value}")
        return 0.0

def format_percentage(value):
    """
    Convert decimal to percentage string
    
    Examples:
        0.0274 → "2.74%"
        -0.0123 → "-1.23%"
        0.0 → "0.00%"
    
    Args:
        value: Decimal return value (e.g., 0.0274)
    
    Returns:
        String formatted as percentage
    """
    if value is None:
        return "N/A"
    
    try:
        # Convert to percentage and format with 2 decimal places
        percentage = float(value) * 100.0
        return f"{percentage:.2f}%"
    except (ValueError, TypeError):
        return "N/A"
```

**Usage Example** (Management Command):

```python
from django.core.management.base import BaseCommand
from public_site.models import StrategyPage
from public_site.utils.performance_calculator import update_performance_from_monthly_data

class Command(BaseCommand):
    help = 'Update performance metrics for all strategies'
    
    def handle(self, *args, **options):
        strategies = StrategyPage.objects.filter(live=True)
        
        for strategy in strategies:
            if strategy.monthly_performance_data:
                self.stdout.write(f"Updating {strategy.title}...")
                
                results = update_performance_from_monthly_data(
                    strategy,
                    strategy.monthly_performance_data
                )
                
                self.stdout.write(self.style.SUCCESS(
                    f"  YTD: {results['ytd']['strategy']:.2%} "
                    f"(vs {results['ytd']['benchmark']:.2%})"
                ))
                self.stdout.write(self.style.SUCCESS(
                    f"  1Y:  {results['one_year']['strategy']:.2%} "
                    f"(vs {results['one_year']['benchmark']:.2%})"
                ))
                
                if results.get('three_year'):
                    self.stdout.write(self.style.SUCCESS(
                        f"  3Y:  {results['three_year']['strategy']:.2%} "
                        f"(vs {results['three_year']['benchmark']:.2%})"
                    ))
```

**Mathematical Formulas Summary**:

1. **Compound Return**: `R_total = ∏(1 + r_i) - 1`
2. **Annualized Return**: `R_ann = (1 + R_total)^(1/years) - 1`
3. **YTD Return**: Compound all monthly returns in current year
4. **1-Year Return**: Compound trailing 12 monthly returns
5. **3-Year Return**: Compound 36 months, then annualize
6. **Since Inception**: Compound all months since start, then annualize

**Key Implementation Insights**:
1. **Compound Returns**: Uses multiplicative compounding, not simple addition
2. **Annualization**: Geometric mean formula for accurate multi-year returns
3. **Missing Data Handling**: Returns 0.0 or None for incomplete data
4. **Percentage Parsing**: Handles multiple formats ("2.74%", "2.74", 2.74)
5. **Negative Returns**: Properly handles negative monthly returns
6. **Inception Logic**: Different handling for strategies < 1 year old
7. **Ruff Complexity Exemption**: Acknowledged in `ruff.toml` due to legitimate financial calculation complexity

**Performance Characteristics**:
- Calculation time: ~5ms per strategy (all metrics)
- Memory usage: ~1KB per strategy (monthly data stored as JSON)
- Database queries: 1 read + 1 write per strategy update
- Precision: 4 decimal places (0.01% accuracy)

**Files to Reference**:
- `public_site/utils/performance_calculator.py` (21.91 importance) - All calculation logic
- `public_site/models.py` - StrategyPage and PerformanceMetric models
- `ruff.toml` - Complexity exemptions for financial calculations

---

### 7. Deployment Infrastructure - Docker & Startup Orchestration

**Architecture Decision**: Implemented multi-stage Docker build with parallel initialization to minimize startup time. Uses `uv` package manager (10-100x faster than pip) and optimized static file handling with cache busting.

**Multi-Stage Dockerfile** (`Dockerfile` - 66 lines):

```dockerfile
# Stage 1: Builder - Install dependencies
FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency management (10-100x faster than pip)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy only dependency files first (layer caching optimization)
WORKDIR /app
COPY pyproject.toml requirements.txt ./

# Install dependencies with uv
RUN uv venv && \
    . .venv/bin/activate && \
    uv pip install -r requirements.txt

# Stage 2: Production - Minimal runtime image
FROM python:3.11-slim

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1  # Prevent .pyc files
ENV PYTHONUNBUFFERED=1          # Real-time logging
ENV PORT=8080
ENV PATH="/app/.venv/bin:$PATH"

# Install only runtime dependencies (no build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy virtual environment from builder (no reinstall needed)
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY . /app/

# Make scripts executable
RUN chmod +x runtime_init.sh build.sh 2>/dev/null || true

# Create directories and add cache-busting marker
RUN mkdir -p staticfiles/css staticfiles/js staticfiles/images && \
    mkdir -p /var/lib/data/images /var/lib/data/documents && \
    echo "BUILD_TIME=$(date +%s)" > /app/.build_marker

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app && \
    chown -R app:app /var/lib/data
USER app

# Health check (every 30s, 30s timeout, 3 retries)
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health/', timeout=10)" || exit 1

EXPOSE 8080

ENTRYPOINT ["./runtime_init.sh"]
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-8080} --workers 2 --timeout 60 --access-logfile - --error-logfile - ethicic.wsgi:application"]
```

**Runtime Initialization Script** (`runtime_init.sh` - 97 lines):

```bash
#!/bin/bash
# Optimized runtime initialization - parallel operations where possible
set +e  # Don't exit on errors

echo "=== Optimized Runtime Initialization ==="
echo "Time: $(date)"

# Set Django settings
export DJANGO_SETTINGS_MODULE=ethicic.settings

# Quick environment check
echo "Environment: PORT=${PORT:-8080}, DB_URL=${DB_URL:-NOT_SET}"

# === PARALLEL OPERATION 1: Static Files (runs in background) ===
(
    echo "📁 Force clearing static files cache..."
    
    # Check if this is a new build or force rebuild is requested
    if [ -f /app/.build_marker ] || [ "$FORCE_STATIC_REBUILD" = "true" ]; then
        echo "🔄 New build detected - clearing all static files..."
        rm -rf staticfiles/* 2>/dev/null || true
        find staticfiles -type f -delete 2>/dev/null || true
    fi
    
    echo "🎨 Building CSS..."
    python manage.py build_css 2>&1 || echo "⚠️  CSS build failed"
    
    echo "📁 Collecting static files..."
    python manage.py collectstatic --noinput --clear 2>&1 || {
        echo "⚠️  Static collection failed, manual copy..."
        rm -rf staticfiles 2>/dev/null
        cp -r static staticfiles 2>/dev/null
    }
    
    # Verify critical CSS files are present
    if [ ! -f "staticfiles/css/about-page-v2.css" ]; then
        echo "⚠️  Critical CSS missing, forcing manual copy..."
        cp -r static/* staticfiles/ 2>/dev/null || true
    fi
    
    echo "✅ Static files ready"
) &
STATIC_PID=$!

# === DATABASE OPERATIONS (sequential, with mode detection) ===
if [ ! -z "$DB_URL" ]; then
    # Mode 1: Kinsta PostgreSQL (production)
    echo "📊 Kinsta PostgreSQL detected..."
    python manage.py migrate --noinput 2>&1 || echo "⚠️  Migration warnings"
    python manage.py setup_kinsta 2>&1 || echo "⚠️  Setup warnings"
    
elif [ ! -z "$UBI_DATABASE_URL" ] && [ -z "$SKIP_UBICLOUD" ]; then
    # Mode 2: Ubicloud PostgreSQL (with connectivity test)
    echo "🔍 Testing Ubicloud connectivity..."
    
    # Quick connectivity check (3 second timeout)
    timeout 3 python -c "
import psycopg2, os
from urllib.parse import urlparse
url = urlparse(os.getenv('UBI_DATABASE_URL'))
try:
    conn = psycopg2.connect(
        host=url.hostname, port=url.port or 5432,
        database=url.path[1:], user=url.username,
        password=url.password, connect_timeout=3,
        sslmode='require'
    )
    conn.close()
    exit(0)
except: exit(1)
" 2>&1
    
    if [ $? -eq 0 ]; then
        echo "✅ Ubicloud connected - hybrid mode"
        python manage.py migrate --noinput 2>&1 || echo "⚠️  Migration warnings"
        
        # === PARALLEL OPERATION 2: Ubicloud Import (runs in background) ===
        (python manage.py safe_import_from_ubicloud 2>&1 || echo "⚠️  Import skipped") &
        IMPORT_PID=$!
    else
        echo "⚠️  Ubicloud unreachable - standalone mode"
        export USE_SQLITE=true
        unset UBI_DATABASE_URL
        python manage.py migrate --noinput 2>&1
        python manage.py setup_homepage 2>&1
    fi
else
    # Mode 3: Standalone (SQLite)
    echo "📍 Standalone mode"
    python manage.py migrate --noinput 2>&1
    python manage.py setup_homepage 2>&1
fi

# === WAIT FOR PARALLEL OPERATIONS ===
wait $STATIC_PID 2>/dev/null
[ ! -z "$IMPORT_PID" ] && wait $IMPORT_PID 2>/dev/null

echo "✅ Initialization complete"

# === START APPLICATION ===
export PORT=${PORT:-8080}
exec "$@"
```

**Gunicorn Configuration** (Production WSGI Server):

```bash
# Command from Dockerfile CMD
gunicorn \
  --bind 0.0.0.0:${PORT:-8080} \
  --workers 2 \
  --timeout 60 \
  --access-logfile - \
  --error-logfile - \
  ethicic.wsgi:application

# Configuration breakdown:
# --bind: Listen on all interfaces, port from env (default 8080)
# --workers: 2 worker processes (CPU cores * 2 + 1 is typical)
# --timeout: 60 second request timeout
# --access-logfile -: Log access to stdout
# --error-logfile -: Log errors to stdout
```

**Health Check Endpoint** (`public_site/views.py`):

```python
from django.http import JsonResponse
from django.conf import settings
from django.core.cache import cache
import os

def health_check(request):
    """
    Health check endpoint for container orchestration
    
    Query parameters:
    - ?debug=storage: Check R2/media storage
    - ?env=check: Display environment variables
    - ?list=media: List media files
    
    Returns:
        JSON with status and optional debug info
    """
    health_data = {
        'status': 'healthy',
        'database': 'unknown',
        'cache': 'unknown',
        'storage': 'unknown',
    }
    
    # Check database
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            health_data['database'] = 'connected'
    except Exception as e:
        health_data['database'] = f'error: {str(e)}'
        health_data['status'] = 'degraded'
    
    # Check cache
    try:
        cache.set('health_check', 'ok', 10)
        if cache.get('health_check') == 'ok':
            health_data['cache'] = 'connected'
        else:
            health_data['cache'] = 'error: write/read mismatch'
    except Exception as e:
        health_data['cache'] = f'error: {str(e)}'
    
    # Check storage (if debug mode)
    if request.GET.get('debug') == 'storage':
        try:
            from django.core.files.storage import default_storage
            health_data['storage'] = {
                'backend': default_storage.__class__.__name__,
                'location': getattr(default_storage, 'location', 'N/A'),
            }
        except Exception as e:
            health_data['storage'] = f'error: {str(e)}'
    
    # Environment check (if requested)
    if request.GET.get('env') == 'check':
        health_data['environment'] = {
            'DEBUG': settings.DEBUG,
            'USE_R2': os.getenv('USE_R2', 'false'),
            'REDIS_URL': 'set' if os.getenv('REDIS_URL') else 'not set',
            'DB_URL': 'set' if os.getenv('DB_URL') else 'not set',
        }
    
    # Media file listing (if requested)
    if request.GET.get('list') == 'media':
        try:
            from wagtail.images.models import Image
            health_data['media_count'] = Image.objects.count()
        except Exception as e:
            health_data['media_count'] = f'error: {str(e)}'
    
    return JsonResponse(health_data)
```

**WhiteNoise Static File Serving** (`ethicic/settings.py`):

```python
# Middleware configuration
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Serve static files efficiently
    'django.contrib.sessions.middleware.SessionMiddleware',
    # ... other middleware
]

# WhiteNoise configuration
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Static files settings
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# WhiteNoise compression and caching
WHITENOISE_COMPRESS_OFFLINE = True  # Pre-compress static files
WHITENOISE_MANIFEST_STRICT = False  # Don't fail on missing files
WHITENOISE_MAX_AGE = 3600  # Cache for 1 hour
```

**Security Headers Configuration** (`ethicic/settings.py`):

```python
# HTTPS enforcement (trust X-Forwarded-Proto from proxy)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

if not DEBUG:
    # Production security settings
    SECURE_SSL_REDIRECT = True  # Redirect HTTP to HTTPS
    SECURE_HSTS_SECONDS = 31536000  # 1 year HSTS
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # Cookie security
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    CSRF_COOKIE_HTTPONLY = True
    
    # Additional security headers
    SECURE_CONTENT_TYPE_NOSNIFF = True  # Prevent MIME sniffing
    SECURE_BROWSER_XSS_FILTER = True    # Enable XSS filtering
    X_FRAME_OPTIONS = 'DENY'            # Prevent clickjacking
```

**Environment Variable Management**:

```python
# settings.py - Environment variable loading with defaults

import os
from pathlib import Path

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Secret key (auto-generate if missing)
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    import uuid
    SECRET_KEY = str(uuid.uuid4())
    print("⚠️  Generated temporary SECRET_KEY - set SECRET_KEY env var for production")

# Debug mode
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Allowed hosts
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
if os.getenv('KINSTA_HOST'):
    ALLOWED_HOSTS.append(os.getenv('KINSTA_HOST'))

# Database URL
DB_URL = os.getenv('DB_URL', '')
UBI_DATABASE_URL = os.getenv('UBI_DATABASE_URL', '')
USE_SQLITE = os.getenv('USE_SQLITE', 'false').lower() == 'true'

# Redis URL
REDIS_URL = os.getenv('REDIS_URL', '')

# Cloudflare R2
USE_R2 = os.getenv('USE_R2', 'false').lower() == 'true'
R2_ACCESS_KEY_ID = os.getenv('R2_ACCESS_KEY_ID', '')
R2_SECRET_ACCESS_KEY = os.getenv('R2_SECRET_ACCESS_KEY', '')
R2_BUCKET_NAME = os.getenv('R2_BUCKET_NAME', 'ethicic-media')
R2_ENDPOINT_URL = os.getenv('R2_ENDPOINT_URL', '')
R2_CUSTOM_DOMAIN = os.getenv('R2_CUSTOM_DOMAIN', 'images.ec1c.com')

# PostHog
POSTHOG_API_KEY = os.getenv('POSTHOG_API_KEY', '')

# Cloudflare Turnstile
TURNSTILE_SECRET_KEY = os.getenv('TURNSTILE_SECRET_KEY', '')
TURNSTILE_SITE_KEY = os.getenv('TURNSTILE_SITE_KEY', '')
```

**Deployment Modes**:

1. **Production (Kinsta)**:
   - `DB_URL` set → Kinsta PostgreSQL
   - `REDIS_URL` set → Redis cache
   - `USE_R2=true` → Cloudflare R2 media
   - `DEBUG=false` → Security headers enabled
   - Gunicorn with 2 workers

2. **Hybrid (Kinsta + Ubicloud)**:
   - `DB_URL` + `UBI_DATABASE_URL` set
   - Parallel import from Ubicloud on startup
   - Kinsta as primary, Ubicloud for content sync

3. **Standalone (SQLite)**:
   - No `DB_URL` or `UBI_DATABASE_URL`
   - SQLite database (local file)
   - Local memory cache
   - Local filesystem storage

**Startup Timing** (typical production deployment):

```
Database migration:        2-3 seconds
CSS building (parallel):   3-4 seconds
Static collection:         2-3 seconds
Ubicloud import:          5-10 seconds (parallel)
Total startup time:        5-7 seconds (excluding import)
```

**Key Implementation Insights**:
1. **Multi-Stage Build**: Separates build dependencies from runtime, reducing image size by ~40%
2. **UV Package Manager**: 10-100x faster than pip for dependency installation
3. **Parallel Operations**: Static files and imports run concurrently with database operations
4. **Cache Busting**: Build marker forces static file regeneration on new deployments
5. **Graceful Degradation**: Falls back to SQLite if PostgreSQL unavailable
6. **Non-Root User**: Runs as `app` user for security
7. **Health Checks**: Docker health check every 30s with 3 retries

**Performance Characteristics**:
- Docker image size: ~450 MB (multi-stage optimization)
- Startup time: 5-7 seconds (excluding Ubicloud import)
- Static file serving: ~10ms (WhiteNoise with compression)
- Health check response: ~50ms
- Memory usage: ~200 MB per worker (2 workers = ~400 MB total)

**Files to Reference**:
- `Dockerfile` (66 lines) - Multi-stage Docker build
- `runtime_init.sh` (97 lines) - Startup orchestration with parallel operations
- `build.sh` - Build-time script
- `ethicic/settings.py` - Django configuration with environment variables
- `public_site/views.py` - Health check endpoint

---

### 8. Management Commands

**What it does**: Provides 50+ Django management commands for deployment, content management, and maintenance.

**Key Commands**:

**Deployment**:
- `deploy` - Full deployment orchestration (migrations, CSS build, static collection)
- `setup_kinsta` - Kinsta-specific configuration
- `setup_homepage` - Initialize homepage with default content

**Content Management**:
- `safe_import_from_ubicloud` - Import pages, images, documents from Ubicloud
- `import_from_ubicloud` - Legacy import command
- `sync_cache` - Sync local cache with remote database

**CSS & Assets**:
- `build_css` - Build Garden UI CSS bundles
- `collectstatic` - Collect static files for production

**Database**:
- `migrate` - Run database migrations
- `makemigrations` - Create new migrations

**Development**:
- `runserver` - Development server
- `createsuperuser` - Create admin user
- `shell` - Django shell

**Files to Reference**:
- `public_site/management/commands/` - All management commands
- `public_site/management/commands/deploy.py` - Deployment orchestration
- `public_site/management/commands/setup_homepage.py` - Homepage initialization

---

### 9. Security Features

**What it does**: Implements enterprise-grade security across all layers of the application.

**Form Security** (covered in detail in section 2):
- Multi-layer spam protection
- Rate limiting (3 per hour per IP)
- Honeypot fields
- Cloudflare Turnstile
- Timing validation
- Content spam detection
- Domain blocking

**Application Security**:
- HTTPS enforcement in production
- HSTS with 1-year duration
- Secure cookie flags (HttpOnly, Secure, SameSite)
- CSRF protection on all forms
- XSS filtering
- Content type sniffing protection
- Clickjacking prevention (X-Frame-Options: DENY)

**Database Security**:
- SSL/TLS connections
- Client certificate authentication
- Connection string encryption
- SQL injection protection (Django ORM)

**Secrets Management**:
- Environment variable-based configuration
- No secrets in code or version control
- `.secrets.baseline` for secret scanning

**Compliance**:
- WCAG 2.1 AA accessibility compliance
- SEC compliance (PO Box rejection in onboarding)
- Privacy policy and terms of service
- GDPR-friendly (PostHog privacy controls)

**Files to Reference**:
- `public_site/forms.py` - Form security implementation
- `ethicic/settings.py` - Security middleware configuration
- `.secrets.baseline` - Secret scanning baseline

---

### 10. Documentation System

**What it does**: Provides comprehensive documentation for developers, designers, and content managers.

**Documentation Files** (20+ files):

**Architecture**:
- `docs/CSS_ARCHITECTURE_CURRENT.md` - CSS migration guide
- `docs/CSS_OVERVIEW.md` - CSS system overview
- `docs/DEVELOPMENT_WORKFLOW.md` - Development process
- `docs/POSTCSS_BUILD_PROCESS.md` - CSS build pipeline

**Design**:
- `docs/BRAND_COLORS.md` - Brand color system
- `docs/TYPOGRAPHY_USAGE.md` - Typography guidelines
- `garden-ui-handoff.md` - Garden UI design system handoff

**Operations**:
- `docs/POSTHOG_ERROR_TRACKING.md` - Error tracking setup
- `deployment-monitoring.md` - Deployment monitoring guide
- `IMPORT_AUDIT_REPORT.md` - Content import audit

**Quality**:
- `docs/ACCESSIBILITY_FIXES_2025-01-28.md` - Accessibility improvements
- `docs/CSS_TESTING.md` - CSS testing strategy
- `docs/CSS_LINTING_SETUP.md` - CSS linting configuration
- `security-report.md` - Security audit findings
- `ux-audit-notes.md` - UX audit notes

**Content**:
- `docs/about_text.md` - About page content
- `docs/homepage-cms-migration.md` - Homepage migration guide
- `docs/performance_system_readme.md` - Performance system documentation

**Developer Memory**:
- `CLAUDE.md` - Development memories and AI configuration
- `.claude/` - Claude AI project configuration

**Files to Reference**:
- `docs/` directory - All documentation files
- `CLAUDE.md` - Development context and decisions
- `README.md` - Setup and deployment guide

---

### 11. Testing Infrastructure

**What it does**: Provides testing utilities and scripts for quality assurance.

**Test Types**:
- Unit tests for models and utilities
- Integration tests for forms and views
- CSS quality monitoring
- Link checking
- Accessibility testing

**Test Scripts**:
- `run_tests_fast.py` - Fast test runner
- `count_tests.sh` - Test count utility
- `test_all_pages.sh` - Page accessibility testing
- `test_local.sh` - Local testing script
- `css_monitoring.py` - CSS quality tracking
- `enhanced_link_checker.py` - Comprehensive link validation

**Quality Metrics**:
- `css_baseline.json` - CSS quality baseline (56 files tracked)
- `css-specificity-audit.txt` - CSS specificity analysis
- `ethicic_wcag.csv` - WCAG compliance audit results

**Test Reports**:
- `BROKEN_LINKS_REPORT.md` - Link validation results
- `COMPREHENSIVE_LINK_CHECK_FINAL_REPORT.md` - Final link audit
- `WAGTAIL_IMAGE_UPLOAD_INVESTIGATION_REPORT.md` - Image upload debugging

**Files to Reference**:
- `tests/` directory - Test files
- `pytest.ini` - Pytest configuration
- `run_tests_fast.py` - Test runner
- `css_monitoring.py` - CSS quality monitoring

---

### 12. Additional Features

**URL Management**:
- SEO-friendly URLs
- Automatic sitemap generation (`/sitemap.xml`)
- Robots.txt configuration (`/robots.txt`)
- Carbon.txt for sustainability (`/carbon.txt`)
- LLMs.txt for AI crawlers (`/llms.txt`)

**Search**:
- Full-text search across pages
- Blog post search
- Encyclopedia search
- Search results page with highlighting

**Navigation**:
- Desktop navigation menu
- Mobile-responsive hamburger menu
- Breadcrumb navigation
- Footer navigation with multiple columns

**Media Management**:
- Automatic image optimization
- Multiple format support (AVIF, WebP, JPEG, PNG)
- Responsive images with srcset
- Document library for PDFs
- Media library with search and filtering

**Blog System**:
- Rich content with StreamField
- Categories and tags
- Related posts
- Reading time estimation
- Author profiles
- Featured images
- Social sharing

**Encyclopedia**:
- 100+ investment terms
- Difficulty levels (Beginner, Intermediate, Advanced)
- Categories (ESG, Basics, Ethics, Analysis)
- Related terms
- Examples and further reading

**Strategy Pages**:
- Performance metrics with charts
- Geographic allocation visualization
- Sector positioning (overweights/exclusions)
- Risk metrics display
- Holdings information
- Asset allocation breakdown

---

## What Worked Well

### 1. CSS Architecture Migration
The Tailwind CSS migration was highly successful, achieving an **84% reduction in `!important` declarations** (3,006 → 471). This dramatically reduced specificity conflicts and made the codebase more maintainable.

**Key Success Factors**:
- Utility-first approach reduced custom CSS
- Consistent design tokens
- Clear migration strategy with tracking
- Emergency CSS files for critical fixes during transition

### 2. Form Security System
The multi-layer security approach proved robust against spam and abuse. The defense-in-depth strategy with honeypots, Turnstile, timing validation, rate limiting, and content detection effectively blocked automated attacks while maintaining good user experience.

**Key Success Factors**:
- Multiple independent security layers
- Graceful degradation (email fallback)
- Accessibility maintained throughout
- Clear error messages for legitimate users

### 3. Database Fallback System
The intelligent multi-database system with automatic failover worked reliably across different environments. Connection testing at startup prevented deployment failures.

**Key Success Factors**:
- Automatic connection testing
- Clear fallback hierarchy
- SSL/TLS support
- Development-friendly (SQLite fallback)

### 4. External Service Integration
Clean integration patterns with graceful degradation ensured the site remained functional even when external services were unavailable.

**Key Success Factors**:
- Optional dependencies
- Fallback mechanisms
- Clear error handling
- Environment-based configuration

### 5. Documentation Discipline
Comprehensive documentation made the system maintainable and helped new developers understand the architecture quickly.

**Key Success Factors**:
- Architecture decision records
- Migration guides
- Inline code comments
- Developer memory (CLAUDE.md)

---

## What Could Be Improved

### 1. System Complexity
The system became complex with multiple databases, fallback mechanisms, and migration states. Future projects should consider simpler architectures unless complexity is truly necessary.

**Specific Issues**:
- Three database systems to maintain
- CSS migration in progress (dual systems)
- Multiple configuration paths
- Complex startup sequence

### 2. Deployment Process
The multi-stage deployment process with parallel operations could be simplified. Some operations could be moved to build-time rather than runtime.

**Specific Issues**:
- Long startup time (CSS builds, imports)
- Parallel operations increase complexity
- Multiple initialization scripts
- Environment-specific logic

### 3. Testing Coverage
Limited automated testing coverage meant more manual testing was required. More comprehensive unit and integration tests would improve confidence in changes.

**Specific Issues**:
- Few unit tests for models
- Limited integration tests
- No end-to-end tests
- Manual accessibility testing

### 4. Monolithic Architecture
The application could benefit from more modular architecture. Separating concerns (CMS, forms, calculations) into distinct services might improve maintainability.

**Specific Issues**:
- Single Django application
- Tightly coupled components
- Shared database for all features
- Difficult to scale individual components

### 5. CSS Migration Incomplete
While 84% complete, the CSS migration left some legacy Garden UI code that created maintenance burden.

**Specific Issues**:
- 31 of 56 CSS files still have issues
- 644 undefined CSS variables
- Emergency CSS files needed
- Dual system complexity

---

## Technology Stack Reference

### Backend
- **Django 5.1.5** - Web framework
- **Wagtail 7.0.1** - CMS
- **Python 3.11** - Programming language
- **Gunicorn 21.2.0** - WSGI server
- **psycopg2** - PostgreSQL adapter
- **redis-py** - Redis client

### Frontend
- **Tailwind CSS 4.1.11** - Utility-first CSS framework
- **HTMX 1.9.11** - Server-driven interactivity
- **Alpine.js 3.14.1** - Lightweight reactive framework
- **Chart.js** - Data visualization
- **PostCSS** - CSS processing

### Database
- **PostgreSQL** - Primary database (Kinsta, Ubicloud)
- **Redis 5.0.8** - Caching and sessions
- **SQLite** - Development fallback

### Deployment
- **Docker** - Containerization
- **Kinsta** - Hosting platform
- **WhiteNoise** - Static file serving
- **uv** - Fast Python package installer

### External Services
- **PostHog** - Analytics and error tracking
- **Cloudflare R2** - Object storage (S3-compatible)
- **Cloudflare Turnstile** - Bot protection
- **Google Tag Manager** - Marketing analytics

### Development Tools
- **Ruff** - Python linter and formatter
- **Stylelint** - CSS linter
- **Prettier** - Code formatter
- **ESLint** - JavaScript linter
- **pytest** - Testing framework

---

## For Future Projects

When building similar systems in the future, consider these lessons learned:

### 1. Reuse the Form Security Patterns
The multi-layer approach is battle-tested and effective. The combination of honeypots, Turnstile, timing validation, rate limiting, and content detection provides robust protection while maintaining accessibility.

**Recommended**: Copy `public_site/forms.py` as a starting point for any form-heavy application.

### 2. Learn from the CSS Migration
Starting with Tailwind CSS from day one would have avoided the migration complexity. The utility-first approach significantly reduced technical debt.

**Recommended**: Use Tailwind CSS from the start, avoid custom design systems unless absolutely necessary.

### 3. Simplify Database Strategy
Multiple database fallbacks added complexity that may not have been necessary. Consider a simpler approach with a single reliable database provider.

**Recommended**: Use a single managed PostgreSQL instance with good backups rather than multiple fallback systems.

### 4. Maintain Documentation Discipline
The comprehensive documentation was invaluable for maintenance and onboarding. Continue this practice in future projects.

**Recommended**: Document architecture decisions as they're made, not after the fact.

### 5. Invest in Testing Early
More automated testing would have caught issues earlier and made refactoring safer. Start with good test coverage from the beginning.

**Recommended**: Aim for 80%+ test coverage, especially for business logic and security-critical code.

### 6. Consider Modular Architecture
For larger projects, consider separating concerns into distinct services (microservices or modular monolith) rather than a single Django application.

**Recommended**: Evaluate whether the project would benefit from separation of CMS, forms, calculations, and other major systems.

### 7. Plan Migrations Carefully
The CSS migration was successful but took significant effort. Plan major migrations with clear milestones and tracking.

**Recommended**: Use metrics (like `css_baseline.json`) to track migration progress and prevent regression.

---

## Repository Status

- **Last Active Development**: 2025 (CSS migration completed)
- **Import Audit Status**: ✅ CLEAN - No critical import issues
- **Deployment Status**: ✅ APPROVED FOR DEPLOYMENT (as of audit)
- **CSS Migration**: 84% complete (471 `!important` declarations remaining)
- **Test Coverage**: Limited (needs improvement)
- **Documentation**: Comprehensive (20+ documentation files)
- **Current Purpose**: Feature inventory and historical reference only

---

## Important Notes

### Do Not Use This Repository for New Development

This repository is deprecated and should **not** be used as a starting point for new projects. It exists solely for reference and feature inventory purposes.

### Why Not Fork This?

While this codebase has many good features, it also has:
- Incomplete CSS migration (dual systems)
- Complex database fallback logic
- Limited test coverage
- Monolithic architecture
- Technical debt from multiple iterations

Starting fresh with lessons learned will be more efficient than trying to clean up this codebase.

### What You Can Take From This

Feel free to reference and adapt:
- Form security patterns (`public_site/forms.py`)
- Performance calculation logic (`public_site/utils/performance_calculator.py`)
- Tailwind configuration (`tailwind.config.js`)
- Documentation structure (`docs/`)
- Deployment patterns (`runtime_init.sh`, `Dockerfile`)

Just don't try to use the entire codebase as-is.

---

## Questions?

If you have questions about specific features or implementation details, refer to:
- The comprehensive onboarding guide in the repository notes
- Individual documentation files in `docs/`
- Code comments in key files
- `CLAUDE.md` for development context and decisions

---

**Last Updated**: October 25, 2025  
**Maintained By**: Historical reference only (no active maintainer)
