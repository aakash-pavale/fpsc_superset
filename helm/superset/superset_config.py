import os
import sys
import logging
import traceback
import urllib.parse
from sqlalchemy import create_engine

# --- DATABASE ---
# Updated with correct password
SQLALCHEMY_DATABASE_URI = "postgresql://superset_admin:CHANGE_ME_PASSWORD@fpsc-superset-db.postgres.database.azure.com:5432/superset?sslmode=require"

# DIAGNOSTIC CONNECTION TEST
sys.stderr.write("\n--- DIAGNOSTIC: STARTING DB CONNECTION TEST ---\n")
try:
    engine = create_engine(SQLALCHEMY_DATABASE_URI)
    sys.stderr.write(f"--- DIAGNOSTIC: Engine created for {engine.url.host}\n")
    with engine.connect() as conn:
        sys.stderr.write("--- DIAGNOSTIC: CONNECTION SUCCESSFUL! ---\n")
except Exception as e:
    sys.stderr.write("--- DIAGNOSTIC: CONNECTION FAILED ---\n")
    sys.stderr.write(f"ERROR TYPE: {type(e).__name__}\n")
    sys.stderr.write(f"ERROR MESSAGE: {str(e)}\n")
    traceback.print_exc(file=sys.stderr)
sys.stderr.write("--- DIAGNOSTIC: END OF TEST ---\n\n")
sys.stderr.flush()

# --- BRANDING ---
APP_NAME = "FPS Analytics"
APP_ICON = "/static/assets/images/fps_analytics/logo.png"
FAVICONS = [{"href": "/static/assets/images/fps_analytics/favicon/favicon.png"}]
LOGO_TOOLTIP = "FPS Analytics"
LOGO_RIGHT_TEXT = "Analytics"

# Override the default loading GIF
EXTRA_CSS = """
    .loading-img {
        background-image: url("/static/assets/images/fps_analytics/loading/loading.gif") !important;
        background-size: contain;
    }
"""

THEME_OVERRIDES = {
    "colors": {
        "primary": {"base": '#101F5B'},
        "secondary": {"base": '#FF6E13'},
        "success": {"base": '#2E7D32'},
        "warning": {"base": '#F9A825'},
        "error": {"base": '#C62828'},
    }
}

EXTRA_CATEGORICAL_COLOR_SCHEMES = [
    {
        "id": "fps_primary_01_colors",
        "label": "FPS Primary 01 Color palette",
        "colors": ["#dcedff", "#b1c0f5", "#6a7fc0", "#14a5ff", "#1457ff", "#013099", "#14167b", "#101f5b", "#011033", "#000919"]
    },
    {
        "id": "fps_primary_02_colors",
        "label": "FPS Primary 02 Color palette",
        "colors": ["#ffffff", "#e6e6e6", "#b8bfcc", "#828a99", "#6d7480", "#575d66", "#4e5259", "#43464d", "#373a40", "#2c2e33", "#212326", "#16171a"]
    },
    {
        "id": "fps_secondary_colors",
        "label": "FPS Secondary Color palette",
        "colors": ["#ff7c2b", "#ff6e13", "#e36111", "#a1450c"]
    }
]

# --- REDIS & CACHING ---
# Azure Redis requires SSL (port 6380 and rediss:// protocol)
REDIS_HOST = "fpsc-superset-redis.redis.cache.windows.net"
REDIS_PASS = os.environ.get("REDIS_PASSWORD", "PLACEHOLDER")
ENCODED_REDIS_PASS = urllib.parse.quote_plus(REDIS_PASS)
# Use rediss:// and port 6380 for Azure Redis
REDIS_URL = f"rediss://:{ENCODED_REDIS_PASS}@{REDIS_HOST}:6380/0"

CACHE_CONFIG = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": 300,
    "CACHE_KEY_PREFIX": "superset_results",
    "CACHE_REDIS_URL": REDIS_URL,
}
DATA_CACHE_CONFIG = CACHE_CONFIG

# --- SECURITY ---
SECRET_KEY = os.environ.get("SUPERSET_SECRET_KEY", "fpsc_superset_secret_key_123")
ENABLE_PROXY_FIX = True
WEB_EXTERNAL_URL = "https://dashboards.firstprofessional.net"
PREFERRED_URL_SCHEME = "https"

# Fix for KeyError: 'RECAPTCHA_PUBLIC_KEY'
RECAPTCHA_PUBLIC_KEY = ""
RECAPTCHA_PRIVATE_KEY = ""

# --- AUTHENTICATION ---
from flask_appbuilder.security.manager import AUTH_OAUTH
AUTH_TYPE = AUTH_OAUTH
AUTH_USER_REGISTRATION = True
AUTH_USER_REGISTRATION_ROLE = "Admin"

OAUTH_PROVIDERS = [{
    "name": "azure",
    "icon": "fa-windows",
    "token_key": "access_token",
    "remote_app": {
        "client_id": os.environ.get("AZURE_CLIENT_ID"),
        "client_secret": os.environ.get("AZURE_CLIENT_SECRET"),
        "api_base_url": f"https://login.microsoftonline.com/{os.environ.get('AZURE_TENANT_ID')}/v2.0/",
        "client_kwargs": {"scope": "openid email profile"},
        "access_token_url": f"https://login.microsoftonline.com/{os.environ.get('AZURE_TENANT_ID')}/oauth2/v2.0/token",
        "authorize_url": f"https://login.microsoftonline.com/{os.environ.get('AZURE_TENANT_ID')}/oauth2/v2.0/authorize",
    },
}]
