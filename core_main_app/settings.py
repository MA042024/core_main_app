""" Settings for core_main_app.

Settings with the following syntax can be overwritten at the project level:
SETTING_NAME = getattr(settings, "SETTING_NAME", "Default Value")
"""
import os
from os.path import join

from django.conf import settings

if not settings.configured:
    settings.configure()

CUSTOM_NAME = getattr(settings, "CUSTOM_NAME", "Local")
""" :py:class:`str`: Name of the local instance
"""

SERVER_URI = getattr(settings, "SERVER_URI", "http://127.0.0.1:8000")
""" :py:class:`str`: Server URI for import reference.
"""

INSTALLED_APPS = getattr(settings, "INSTALLED_APPS", [])
""" :py:class:`list`: List of apps installed.
"""

# Choose from:  black, black-light, blue, blue-light, green, green-light, purple, purple-light, red, red-light, yellow,
#               yellow-light
WEBSITE_ADMIN_COLOR = getattr(settings, "WEBSITE_ADMIN_COLOR", "yellow")
""" :py:class:`str`: color of the admin dashboard.
"""

# XML
XERCES_VALIDATION = getattr(settings, "XERCES_VALIDATION", False)
""" :py:class:`bool`: Enables Xerces validation (requires additional packages).
"""

# GridFS
GRIDFS_DATA_COLLECTION = getattr(settings, "GRIDFS_DATA_COLLECTION", "fs_data")
""" :py:class:`str`: Collection name for file storage in MongoDB.
"""

# Celery configuration
USE_BACKGROUND_TASK = getattr(settings, "USE_BACKGROUND_TASK", False)
""" :py:class:`bool`: Define use of celery for background tasks.
"""

# SMTP Configuration
USE_EMAIL = getattr(settings, "USE_EMAIL", False)
""" :py:class:`bool`: Activate email sending on the platform.
"""

SERVER_EMAIL = getattr(settings, "SERVER_EMAIL", "root@localhost")
""" :py:class:`str`: Email address sending the message.
"""

ADMINS = getattr(settings, "ADMINS", [])
""" :py:class:`list`: Email addresses of admins.
"""

MANAGERS = getattr(settings, "MANAGERS", [])
""" :py:class:`list`: Email addresses of moderators (managers). 
"""

EMAIL_SUBJECT_PREFIX = getattr(settings, "EMAIL_SUBJECT_PREFIX", "[CURATOR] ")
""" :py:class:`str`: Prefix for easy classification of emails.
"""

MONGO_HOST = getattr(settings, "MONGO_HOST", "localhost")
""" :py:class:`str`: MongoDB host.
"""

MONGO_PORT = getattr(settings, "MONGO_PORT", "27017")
""" :py:class:`str`: MongoDB port.
"""

MONGO_USER = getattr(settings, "MONGO_USER", "")
""" :py:class:`str`: MongoDB user.
"""

MONGO_PASSWORD = getattr(settings, "MONGO_PASSWORD", "")
""" :py:class:`str`: MongoDB password.
"""

MONGO_DB = getattr(settings, "MONGO_DB", "cdcs")
""" :py:class:`str`: MongoDB database.
"""

mongodb_uri_default = (
    f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}"
)

MONGODB_URI = getattr(settings, "MONGODB_URI", mongodb_uri_default)
""" :py:class:`str`: MongoDB connection URI. Automatically generated from other parameters.
"""

USE_TZ = getattr(settings, "USE_TZ", True)
""" :py:class:`bool`: Activate use of timezones.
"""

SEARCHABLE_DATA_OCCURRENCES_LIMIT = getattr(
    settings, "SEARCHABLE_DATA_OCCURRENCES_LIMIT", None
)
""" :py:class:`int` | :py:attr:`None`: Limit for number of occurent to be returned by a search.
"""

BLOB_HOST = getattr(settings, "BLOB_HOST", "GRIDFS")
""" :py:class:`str`: Type of file storage.
"""

BLOB_HOST_URI = getattr(settings, "BLOB_HOST_URI", MONGODB_URI)
""" :py:class:`str`: File storage system URI.
"""

BLOB_HOST_USER = getattr(settings, "BLOB_HOST_USER", None)
""" :py:class:`str`: User for file storage.
"""

BLOB_HOST_PASSWORD = getattr(settings, "BLOB_HOST_PASSWORD", None)
""" :py:class:`str`: Password for file storage.
"""

# Lock
LOCK_OBJECT_TTL = getattr(settings, "LOCK_OBJECT_TTL", 600)  # 10 min
""" :py:class:`int`: Lock duration on files.
"""

# Results per page for paginator
RESULTS_PER_PAGE = getattr(settings, "RESULTS_PER_PAGE", 10)
""" :py:class:`int`: Results per page.
"""

CAN_SET_PUBLIC_DATA_TO_PRIVATE = getattr(
    settings, "CAN_SET_PUBLIC_DATA_TO_PRIVATE", True
)
""" :py:class:`bool`: Can set public data to private.
"""

DEFAULT_DATA_RENDERING_XSLT = getattr(
    settings,
    "DEFAULT_DATA_RENDERING_XSLT",
    join("core_main_app", "common", "xsl", "xml2html.xsl"),
)
""" :py:class:`str`: Path to default XSLT to render data.
"""

# Can anonymous access public document
CAN_ANONYMOUS_ACCESS_PUBLIC_DOCUMENT = getattr(
    settings, "CAN_ANONYMOUS_ACCESS_PUBLIC_DOCUMENT", False
)
""" :py:class:`bool`: Can anonymous user access public document.
"""

DISPLAY_NIST_HEADERS = getattr(settings, "DISPLAY_NIST_HEADERS", False)
""" :py:class:`bool`: HTML pages show the NIST headers/footers.
"""

# Locale folder
BASE_DIR = getattr(
    settings, "BASE_DIR", os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
""" :py:class:`str`: Project installation directory.
"""

LOCALE_PATHS = getattr(
    settings, "LOCALE_PATHS", (os.path.join(BASE_DIR, "core_main_app/locale"),)
)
""" :py:class:`list`: Path for translation messages.
"""

CAN_SET_WORKSPACE_PUBLIC = getattr(settings, "CAN_SET_WORKSPACE_PUBLIC", True)
""" :py:class:`bool`: Can set workspace public.
"""

SSL_CERTIFICATES_DIR = getattr(settings, "SSL_CERTIFICATES_DIR", True)
""" :py:class:`str`: SSL certificates directory location.
"""

XSD_URI_RESOLVER = getattr(settings, "XSD_URI_RESOLVER", None)
""" :py:class:`str`: XSD URI Resolver for lxml validation. Choose from:  None, 'REQUESTS_RESOLVER'.
"""

XML_POST_PROCESSOR = getattr(settings, "XML_POST_PROCESSOR", "NUMERIC")
""" :py:class:`str`: post processor for xml to dict, choose between 'NUMERIC' and 'NUMERIC_AND_STRING' .
    'NUMERIC' convert numeric values from the xml document to integer or float.
    'NUMERIC_AND_STRING' convert numeric values and also store string representation .
"""

VERIFY_DATA_ACCESS = getattr(settings, "VERIFY_DATA_ACCESS", False)
""" :py:class:`bool`: Verify that data returned by a query can be accessed.
"""

DATA_SORTING_FIELDS = getattr(settings, "DATA_SORTING_FIELDS", [])
""" ::py:class:`str` Set the default sort fields for the data query. all the field must 
    be prefixed by "+" or "-" (asc or desc sort) the sort can be multi field and each 
    field must be delimited by "," (ex. ["-title","+name","+date"]) 
"""

AUTO_SET_PID = getattr(settings, "AUTO_SET_PID", False)
""" :py:class:`bool`: Enable PID auto-setting from core_linked_records_app.
"""

PASSWORD_RESET_DOMAIN_OVERRIDE = getattr(
    settings, "PASSWORD_RESET_DOMAIN_OVERRIDE", None
)
""" :py:class:`str`: Override domain of reset password email (e.g. localhost:8000)
"""

ENABLE_SAML2_SSO_AUTH = getattr(settings, "ENABLE_SAML2_SSO_AUTH", False)
""" :py:class:`bool`: Enable SAML2 SSO Authentication
"""
