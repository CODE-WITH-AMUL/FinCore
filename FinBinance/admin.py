# settings.py (or jazzmin_settings.py)
JAZZMIN_SETTINGS = {
    # ─── Branding ────────────────────────────────────────────────
    "site_title": "FinCore Admin",
    "site_header": "FinCore",
    "site_brand": "FinCore",
    "site_logo": "images/logo.png",
    "login_logo": "images/logo.png",
    "login_logo_dark": "images/logo_dark.png",
    "site_logo_classes": "img-circle elevation-3",
    "site_icon": "images/favicon.ico",          # add this file
    "welcome_sign": "Welcome to FinCore — Financial Management & Reporting",
    "copyright": "FinCore Ltd © 2025",

    # ─── Search ─────────────────────────────────────────────────
    "search_model": ["auth.User", "finance.Customer", "finance.Invoice"],

    # ─── Avatars ────────────────────────────────────────────────
    # Use a field on your custom User model, e.g. "avatar"
    # Set to None if you don't have one.
    "user_avatar": None,

    # ─── Top Menu ───────────────────────────────────────────────
    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Support", "url": "https://github.com/your-username/fincore/issues",
         "new_window": True, "icon": "fas fa-life-ring"},
        {"model": "auth.User"},
        {"app": "finance"},
    ],

    # ─── User Menu (top-right dropdown) ─────────────────────────
    "usermenu_links": [
        {"name": "Support", "url": "https://github.com/your-username/fincore/issues",
         "new_window": True, "icon": "fas fa-life-ring"},
        {"model": "auth.user"},
    ],

    # ─── Side Menu ──────────────────────────────────────────────
    "show_sidebar": True,
    "navigation_expanded": False,               # keep collapsed in prod
    "hide_apps": [],
    "hide_models": [],

    "order_with_respect_to": [
        "auth",
        "finance",
        "finance.Company",
        "finance.Revenue",
        "finance.Expense",
        "finance.Customer",
        "finance.Supplier",
        "finance.Invoice",
        "finance.Payment",
        "finance.Investment",
        "finance.Tax",
    ],

    # ─── Custom Links ───────────────────────────────────────────
    # NOTE: "admin:finance_report" must be a real registered URL,
    # otherwise Django will raise NoReverseMatch. Either register it
    # in urls.py, or point to a concrete path.
    "custom_links": {
        "finance": [{
            "name": "Financial Reports",
            "url": "/admin/finance/reports/",   # or "admin:finance_report"
            "icon": "fas fa-chart-line",
            "permissions": ["finance.view_report"]
        }]
    },

    # ─── Icons ──────────────────────────────────────────────────
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "finance": "fas fa-coins",
        "finance.Company": "fas fa-building",
        "finance.Revenue": "fas fa-arrow-up",
        "finance.Expense": "fas fa-arrow-down",
        "finance.Customer": "fas fa-user-tie",
        "finance.Supplier": "fas fa-truck",
        "finance.Invoice": "fas fa-file-invoice-dollar",
        "finance.Payment": "fas fa-credit-card",
        "finance.Investment": "fas fa-chart-pie",
        "finance.Tax": "fas fa-percent",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",

    # ─── Related Modal ──────────────────────────────────────────
    "related_modal_active": True,

    # ─── UI Tweaks ──────────────────────────────────────────────
    # Point to real static files in production for branding/analytics
    "custom_css": "css/admin_custom.css",       # optional
    "custom_js": "js/admin_custom.js",          # optional
    "use_google_fonts_cdn": True,
    "show_ui_builder": False,                   # ← MUST be False in prod

    # ─── Change Form ────────────────────────────────────────────
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "auth.user": "collapsible",
        "auth.group": "vertical_tabs",
    },

    # ─── Localization ───────────────────────────────────────────
    "language_chooser": False,
}

# ─── Optional: Jazzmin UI tweaks (theme) ────────────────────────
JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-dark",
    "accent": "accent-primary",
    "navbar": "navbar-dark navbar-primary",
    "no_navbar_border": True,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": True,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "default",
    "dark_mode_theme": "darkly",
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success",
    },
}