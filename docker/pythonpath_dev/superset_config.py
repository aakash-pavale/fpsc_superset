# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
# This file is included in the final Docker image and SHOULD be overridden when
# deploying the image to prod. Settings configured here are intended for use in local
# development environments. Also note that superset_config_docker.py is imported
# as a final step as a means to override "defaults" configured here
#
import logging
import os
import sys

from celery.schedules import crontab
from flask_caching.backends.filesystemcache import FileSystemCache

logger = logging.getLogger()

DATABASE_DIALECT = os.getenv("DATABASE_DIALECT")
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_PORT = os.getenv("DATABASE_PORT")
DATABASE_DB = os.getenv("DATABASE_DB")

EXAMPLES_USER = os.getenv("EXAMPLES_USER")
EXAMPLES_PASSWORD = os.getenv("EXAMPLES_PASSWORD")
EXAMPLES_HOST = os.getenv("EXAMPLES_HOST")
EXAMPLES_PORT = os.getenv("EXAMPLES_PORT")
EXAMPLES_DB = os.getenv("EXAMPLES_DB")

# The SQLAlchemy connection string.
SQLALCHEMY_DATABASE_URI = (
    f"{DATABASE_DIALECT}://"
    f"{DATABASE_USER}:{DATABASE_PASSWORD}@"
    f"{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_DB}"
)

# Use environment variable if set, otherwise construct from components
# This MUST take precedence over any other configuration
SQLALCHEMY_EXAMPLES_URI = os.getenv(
    "SUPERSET__SQLALCHEMY_EXAMPLES_URI",
    (
        f"{DATABASE_DIALECT}://"
        f"{EXAMPLES_USER}:{EXAMPLES_PASSWORD}@"
        f"{EXAMPLES_HOST}:{EXAMPLES_PORT}/{EXAMPLES_DB}"
    ),
)


REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_CELERY_DB = os.getenv("REDIS_CELERY_DB", "0")
REDIS_RESULTS_DB = os.getenv("REDIS_RESULTS_DB", "1")

RESULTS_BACKEND = FileSystemCache("/app/superset_home/sqllab")

CACHE_CONFIG = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": 300,
    "CACHE_KEY_PREFIX": "superset_",
    "CACHE_REDIS_HOST": REDIS_HOST,
    "CACHE_REDIS_PORT": REDIS_PORT,
    "CACHE_REDIS_DB": REDIS_RESULTS_DB,
}
DATA_CACHE_CONFIG = CACHE_CONFIG
THUMBNAIL_CACHE_CONFIG = CACHE_CONFIG


class CeleryConfig:
    broker_url = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_CELERY_DB}"
    imports = (
        "superset.sql_lab",
        "superset.tasks.scheduler",
        "superset.tasks.thumbnails",
        "superset.tasks.cache",
    )
    result_backend = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_RESULTS_DB}"
    worker_prefetch_multiplier = 1
    task_acks_late = False
    beat_schedule = {
        "reports.scheduler": {
            "task": "reports.scheduler",
            "schedule": crontab(minute="*", hour="*"),
        },
        "reports.prune_log": {
            "task": "reports.prune_log",
            "schedule": crontab(minute=10, hour=0),
        },
    }


CELERY_CONFIG = CeleryConfig

FEATURE_FLAGS = {"ALERT_REPORTS": True}
ALERT_REPORTS_NOTIFICATION_DRY_RUN = True
WEBDRIVER_BASEURL = f"http://superset_app{os.environ.get('SUPERSET_APP_ROOT', '/')}/"  # When using docker compose baseurl should be http://superset_nginx{ENV{BASEPATH}}/  # noqa: E501
# The base URL for the email report hyperlinks.
WEBDRIVER_BASEURL_USER_FRIENDLY = (
    f"http://localhost:8888/{os.environ.get('SUPERSET_APP_ROOT', '/')}/"
)
SQLLAB_CTAS_NO_LIMIT = True

log_level_text = os.getenv("SUPERSET_LOG_LEVEL", "INFO")
LOG_LEVEL = getattr(logging, log_level_text.upper(), logging.INFO)

if os.getenv("CYPRESS_CONFIG") == "true":
    # When running the service as a cypress backend, we need to import the config
    # located @ tests/integration_tests/superset_test_config.py
    base_dir = os.path.dirname(__file__)
    module_folder = os.path.abspath(
        os.path.join(base_dir, "../../tests/integration_tests/")
    )
    sys.path.insert(0, module_folder)
    from superset_test_config import *  # noqa

    sys.path.pop(0)

#
# Optionally import superset_config_docker.py (which will have been included on
# the PYTHONPATH) in order to allow for local settings to be overridden
#
try:
    import superset_config_docker
    from superset_config_docker import *  # noqa: F403

    logger.info(
        "Loaded your Docker configuration at [%s]", superset_config_docker.__file__
    )
except ImportError:
    logger.info("Using default Docker config...")

# ---------------------------------------------------
# Embedding Configuration
# ---------------------------------------------------

# Feature Flags
# Merging with existing flags instead of overwriting
FEATURE_FLAGS.update({
    "EMBEDDED_SUPERSET": True
})

# CORS Enabling
ENABLE_CORS = True
CORS_OPTIONS = {
    "supports_credentials": True,
    "allow_headers": "*",
    "expose_headers": "*",
    "resources": "*",
    "origins": ["http://localhost:4200", "http://localhost:3000"]  # 4200 for angular, 3000 for react
}

# Dashboard embedding
GUEST_ROLE_NAME = "Gamma"
GUEST_TOKEN_JWT_SECRET = "fnklSuYC060W56sSsAfD7Hu/BV64PmdOZdPSRVD+xFYiFwT9HoxLCqzF"
GUEST_TOKEN_JWT_ALGO = "HS256"
GUEST_TOKEN_HEADER_NAME = "X-GuestToken"
GUEST_TOKEN_JWT_EXP_SECONDS = 300  # 5 minutes

# ---------------------------------------------------
# Branding & Customization
# ---------------------------------------------------
APP_NAME = "FPS Analytics"
APP_ICON = "/static/assets/images/fps_analytics/logo.png"
LOGO_TARGET_PATH = '/'
LOGO_TOOLTIP = "FPS Analytics"
LOGO_RIGHT_TEXT = "Analytics"

FAVICONS = [{"href": "/static/assets/images/fps_analytics/favicon/favicon.png"}]

THEME_OVERRIDES = {
    "colors": {
        "primary": {
            "base": '#101F5B',
        },
        "secondary": {
            "base": '#FF6E13',
        },
        "success": {
            "base": '#2E7D32',
        },
        "warning": {
            "base": '#F9A825',
        },
        "error": {
            "base": '#C62828',
        },
        "grayscale": {
            "light5": '#FFFFFF',
        }
    },
    "typography": {
        "families": {
            "sansSerif": 'Inter, "Helvetica Neue", Arial, sans-serif',
            "monospace": '"Source Code Pro", Menlo, Monaco, Consolas, "Courier New", monospace',
        }
    }
}

# ---------------------------------------------------
# CSP Configuration (Fixing WebSocket Errors)
# ---------------------------------------------------
TALISMAN_CONFIG = {
    "content_security_policy": {
        "base-uri": ["'self'"],
        "default-src": ["'self'"],
        "img-src": ["'self'", "blob:", "data:", "http://localhost:9000", "http://localhost:8088"],
        "worker-src": ["'self'", "blob:"],
        "connect-src": [
            "'self'",
            "http://localhost:9000",
            "ws://localhost:9000",
            "https://api.mapbox.com",
            "https://events.mapbox.com",
        ],
        "object-src": ["'none'"],
        "style-src": ["'self'", "'unsafe-inline'"],
        "script-src": ["'self'", "'unsafe-inline'", "'unsafe-eval'"],
    },
    "force_https": False,
    "force_file_save": False,
}

TALISMAN_ENABLED = True

# Disable CSP to fix WebSocket connection in Dev Mode
TALISMAN_ENABLED = False

# ---------------------------------------------------
# Custom Color Palettes
# ---------------------------------------------------
EXTRA_CATEGORICAL_COLOR_SCHEMES = [
    {
        "id": "fps_primary_01_colors",
        "description": "",
        "label": "FPS Primary 01 Color palette",
        "colors": [
            "#dcedff",
            "#b1c0f5",
            "#6a7fc0",
            "#14a5ff",
            "#1457ff",
            "#013099",
            "#14167b",
            "#101f5b",
            "#011033",
            "#000919"
        ]
    },
    {
        "id": "fps_primary_02_colors",
        "description": "",
        "label": "FPS Primary 02 Color palette",
        "colors": [
            "#ffffff",
            "#e6e6e6",
            "#b8bfcc",
            "#828a99",
            "#6d7480",
            "#575d66",
            "#4e5259",
            "#43464d",
            "#373a40",
            "#2c2e33",
            "#212326",
            "#16171a"
        ]
    },
    {
        "id": "fps_secondary_colors",
        "description": "",
        "label": "FPS Secondary Color palette",
        "colors": [
            "#ff7c2b",
            "#ff6e13",
            "#e36111",
            "#a1450c"
        ]
    }
]
