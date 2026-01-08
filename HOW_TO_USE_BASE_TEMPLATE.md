# How to Use the Base Template

## What I Created

I created a **base.html** template at `/pra/templates/base.html` that contains:
- ✅ Common HTML structure
- ✅ Common fonts (Cormorant Garamond + Inter)
- ✅ Common header with navigation
- ✅ Session checking JavaScript (shows "Hi, [Name]" when logged in)
- ✅ Logout functionality

## How to Convert Your Pages

### Template Structure

Instead of having each page with full HTML structure, use this pattern:

```jinja2
{% extends "base.html" %}

{% block title %}Your Page Title{% endblock %}

{% block extra_css %}
<style>
    /* Your page-specific CSS here */
</style>
{% endblock %}

{% block content %}
    <!-- Your page HTML content here -->
    <!-- NO NEED for <header>, fonts, or session checking -->
{% endblock %}

{% block extra_js %}
<script>
    // Your page-specific JavaScript here
    // Session checking is already in base.html
</script>
{% endblock %}
```

## Step-by-Step Conversion Guide

### For Each Page, Follow These Steps:

1. **Remove** everything before `<body>` content (lines 1-40 typically)
2. **Remove** the `<header>` section (the navigation header)
3. **Remove** the session checking JavaScript at the end
4. **Add** `{% extends "base.html" %}` at the very top
5. **Wrap** page-specific CSS in `{% block extra_css %}`
6. **Wrap** main content in `{% block content %}`
7. **Wrap** page-specific JS in `{% block extra_js %}`

## Example: Converting todays_deals.html

### BEFORE (Old Way - Full HTML):
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Today's Deals | SkinRoutine</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/main.css') }}">
    <link href="https://fonts.googleapis.com/css2?family=Inter...">
    <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond...">
    <style>
        .deals-container { ... }
        .page-title { ... }
    </style>
</head>
<body>
    <header class="header">
        <div class="header-container">
            <div class="header-logo">...</div>
            <nav class="header-nav">...</nav>
            <div class="header-actions" id="headerActions">...</div>
        </div>
    </header>

    <div class="deals-container">
        <h1>Today's Deals</h1>
        <!-- content -->
    </div>

    <script>
        // Session checking code...
        async function checkUserSession() { ... }
        async function logout() { ... }
        checkUserSession();

        // Page-specific code
        function refreshDeals() { ... }
    </script>
</body>
</html>
```

### AFTER (New Way - Extends Base):
```jinja2
{% extends "base.html" %}

{% block title %}Today's Deals | SkinRoutine{% endblock %}

{% block extra_css %}
<style>
    .deals-container { ... }
    .page-title { ... }
</style>
{% endblock %}

{% block content %}
<div class="deals-container">
    <h1>Today's Deals</h1>
    <!-- content -->
</div>
{% endblock %}

{% block extra_js %}
<script>
    // Only page-specific code
    function refreshDeals() { ... }
</script>
{% endblock %}
```

## What Gets Removed When Converting

### ❌ REMOVE (Already in base.html):
- `<!DOCTYPE html>`
- `<html>`, `<head>`, `<body>` tags
- Font links (Cormorant Garamond, Inter)
- `main.css` link
- `<header>` section with navigation
- `checkUserSession()` function
- `logout()` function
- `checkUserSession()` call

### ✅ KEEP (Page-specific):
- Page title (in `{% block title %}`)
- Page-specific CSS styles (in `{% block extra_css %}`)
- Main content (in `{% block content %}`)
- Page-specific JavaScript (in `{% block extra_js %}`)

## Pages to Convert

Here's the list of pages that should be converted:

1. ✅ `base.html` - Created (the common template)
2. ⏳ `todays_deals.html` - Convert to extend base
3. ⏳ `build_routine.html` - Convert to extend base
4. ⏳ `routine_results.html` - Convert to extend base
5. ⏳ `deals_comparison.html` - Convert to extend base
6. ⏳ `community.html` - Convert to extend base
7. ⏳ `shopping_list.html` - Convert to extend base
8. ⏳ `deal_finder.html` - Convert to extend base
9. ❌ `auth.html` - Keep as is (special login page, different layout)
10. ❌ `index.html` - Keep as is (landing page, different layout)

## Benefits

✅ **Single Source of Truth**: Header/fonts/session logic in one place
✅ **Easy Updates**: Change header once, applies to all pages
✅ **Consistent Theme**: All pages automatically match
✅ **Less Code**: Each page is much shorter
✅ **Maintainable**: Fix bugs once instead of in every file

## Example File

I created `EXAMPLE_todays_deals_with_base.html` showing how todays_deals.html would look after conversion.

## Need Help?

If you want me to convert all the pages automatically, just say:
**"Convert all pages to use base template"**

Or if you want to do it manually, follow this guide for each page!
