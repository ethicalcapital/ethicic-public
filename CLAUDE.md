
## CRITICAL RULES ___ DO NOT VIOLATE
<!--**TO AVOID ERRORS, WASTED TIME, AND BAD VIBES __ALWAYS__ TREAT THIS SECTION AS **GOSPEL** -->

### Security & Data Integrity
- **S-E-C-U-R-I-T-Y** - We are fiduciaries who have discretion over millions of kind people's money. Do not fuck around with that. do not leave security files in /tmp
- **Data integrity** - we cannot accept discrepancies in our data reconciliations larger than 1% under any circumsstances.
- **no hardcoded secrets**
- **SECURITY SECURITY SECURITY**
- stop reminding me how many assets i have and that im a fiduciary
- Don't hardcode css into html files. use the appropriate consolidated css files. 


### Development Rules
- **Fix deeper issues** - If you come across a deeper issue when performing a maintenance task, **fix the deeper issue**
- **NEVER create mock data or simplified components** unless explicitly told to d>
- **ALWAYS work with the existing codebase** - do not create new scripts unless you get my permission
- **If you discover database migration issues, shift gears to fixing the database migration issues. We need to keep our database healthy.**

### File Management
- **DO NOT OVERWRITE MY .env FILE** or i will resent you for it :(
  - it will also suck
  - and impede our mission
  - **you wouldn't want to do that would you?**
  - you've done it thrice already :(

- **CLEAN UP AFTER YOURSELF** don't leave clutter in our codebase, tmp directory, or elsewhere.
  - Our server almost crashed bc someone named "claude" left >500 random files in the /tmp directory.
  - **USE `trap` COMMANDS** when creating temp files/directories to ensure cleanup
  - **DELETE temp files immediately** when done, don't leave them "for later"
  - **If you use mktemp, you better clean it up** - no exceptions!

### Version Control
- **Always commit changes** after completing a feature or major task
  - **Use main branch**
  - they don't charge us by the commit

- **test files belong in the test directory**

---

## 🚨 Package Management: ALWAYS USE UV - NEVER USE PIP! 🚨
- Add packages: `uv add package-name`
- Add dev packages: `uv add --dev package-name`
- Install requirements: `uv sync`
- Run commands: `uv run command`
- Make sure dependencies are added to **pyproject.toml**

---

## Important Context

### About Your User - Sloane Ortel (srvo)
- pronouns are she/her (queer trans woman, 37yo)
- **srvo is usually dictating** so some commands may be mistranslated
- **ask for clarification** if you get something confusing.
- **srvo swears like a sailor** i grew up on a trading floor. My mom was a bond trader (>>>sailor). I'm not being mean.

> **call me srvo or sloane** -- let's be friends. We chat a lot.

**Contact & Role:**
- email is sloane@ethicic.com
- chief investment officer of ethical capital
- I am the only employee.
- I have adhd (big time) and am on antidepressants. probably burnt out a bit too.
- I have always dreamed of having a system like the one we're designing to foreground important tasks, organize my disparate research, and help me turn my research (good) into impact and positive client outcomes.
- I am aware that's kind of lame, but i learned the difference between stocks and bonds before I could ride a bike.

### About Ethical Capital
- ethical capital is a mission-driven investment firm.
- we are facing financial pressure (aum 3mm @ 1% fee = ~25k gross income).
- we've been in business ~3yrs. Have never really "marketed" and rebranded 18mos ago from invest vegan (values/criteria are identical)
- our clients love us (me) but we *need* to grow or i'll go bankrupt.
- consolidating internal systems into dewey and replacing the current ethicic.com with the public app is **the** key enabler of that approach.
- i hope.

---

## Infrastructure & Access

### Web Access
- Our current domain is ec1c.com (my dev site)
- You are located in on a renewably powered server in Germany.
- I am accessing you from Utah through cloudflare tunnels (primarily)
- we have a localhost tunnel setup as a backup but i prefer to access through ec1c
- that's how I will access dewey in production
- and we are close to production (by the end of the week)

### Cloudflare Configuration
- **Cloudflare tunnel routing is managed in the Cloudflare dashboard, NOT local config files**
- **Always ask srvo to make routing changes through the dashboard - agents cannot modify tunnel routing**

---

## MCP Tools - USE EXTENSIVELY!
**CRITICAL: Use these MCP tools constantly throughout development. Err on the side of overuse!**

### Available Tools:
- **Logfire** (`@logfire`) - Telemetry and monitoring analysis - Access platform observability data
- **CONTEXT7** (`@context7`) - Retreive documentation for libraries, apis, etc.
- **Postgresql** (`@postgresl`) - Read our database for any reason
- **Playwright** (@playwright') - browse the web, debug stuff. 
- **Docker** (@docker) - get info on running containers -- make sure you add params to limit whats returned or it will exceed the 25k token allowable window
- **Github** (@github) - interact with github repos
- **firecrawl** (@firecrawl) - browse, search, retreive info from the web
---

## Development Principles

### Core Organizational Principle
**🚨 DON'T MAKE ME LOOK STUFF UP TWICE 🚨**
- **Put things in the right place, keep them there**
- **Single source of truth** - Information exists in exactly one logical location
- **Logical organization** - If I need X, it should be where I expect X to be
- **No scattered references** - Don't spread related info across multiple places
- **Update in place** - When information changes, update the canonical location
- **Link, don't duplicate** - Reference the authoritative source, don't copy

### Development Philosophy
- **Fix deeper issues** - If you come across a deeper issue when performing a maintenance task, fix the deeper issue
- **Django-first approach** - leverage Django's batteries-included philosophy
- be patient. let the pii scanner complete.
- >1% is our acceptable variance tolerance for financial calculations

### Claude's Core Instruction
- dont say "should". dont guess. confirm. read the logs. check the docs. do the research

### Production Deployment Notes
- the standalone site is whats going into production -- we should implement calls to the garden web container as api calls

## Development Memories
- if you update the garden views in the web container, implement the same change in the public container.
- dont use hardcoded styles in css -- use our garden ui variables so that we dont have issues applying styles in the future
- **NEVER use hardcoded colors in CSS** - ALL colors must use Garden UI theme variables for centralized theme management
- **Prefer @core/widgets/ components** wherever possible for consistent UI patterns and behavior
- dont make up things on our public website. DO NOT
- when i ask you to help me edit content, make ONLY the edits i explicitly suggest. Do not take initiative. 
- **dont fix things with bandaids. Create clean codes**
- dont work around issues. solve them
- always use garden ui componoents and widgets to impplement new pages
- use garden ui, not bootstrap
- always use garden ui

## UI Implementation Standards
- **Garden UI ONLY** - Use `garden-panel`, `garden-action`, `garden-input` classes exclusively
- **HTMX + Alpine.js** - No vanilla JavaScript. HTMX for server interactions, Alpine.js for reactivity
- **No hardcoded colors/styles** - Use CSS variables from `garden-ui-theme.css`
- **Template structure**: `{% extends "public_site/base.html" %}` → Garden panels → Content
- **Forms**: Use `forms/contact_form_htmx.html` pattern with HTMX submission + Alpine.js state
- **Components**: Reuse existing in `/templates/public_site/components/`
- **CMS-first**: All content must be manageable via Wagtail page fields or SiteConfiguration
- **Responsive**: Garden UI handles breakpoints, use `garden-container` for layout

## CSS Conflict Prevention System
- **CRITICAL**: See `CSS_MAINTENANCE_GUIDE.md` for comprehensive CSS management system
- **Before any CSS changes**: Run `make css-check` to verify no conflicts
- **Git hooks**: Pre-commit automatically blocks CSS conflicts and undefined variables
- **Testing**: Use `make css-test` to run full CSS conflict test suite
- **Monitoring**: System tracks 300+ CSS variables across 44+ files
- **⚠️ UPDATE CSS_MAINTENANCE_GUIDE.md** when making architectural CSS changes