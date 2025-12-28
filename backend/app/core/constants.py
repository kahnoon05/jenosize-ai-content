"""
Application Constants Module

Centralizes all magic numbers, strings, and constant values used throughout
the application for better maintainability and consistency.
"""

# ============================================
# Reading Time Constants
# ============================================
WORDS_PER_MINUTE = 200
"""Average reading speed in words per minute for reading time calculations"""

MIN_READING_TIME_MINUTES = 1
"""Minimum reading time to display (avoids showing 0 minutes)"""


# ============================================
# Article Content Constants
# ============================================
META_DESCRIPTION_MAX_LENGTH = 160
"""Maximum length for SEO meta descriptions (Google's recommended limit)"""

META_DESCRIPTION_TRUNCATE_LENGTH = 157
"""Length to truncate meta descriptions (leave room for ellipsis)"""

META_DESCRIPTION_FALLBACK_LENGTH = 150
"""Length of content to use for fallback meta description"""

CONTENT_PREVIEW_LENGTH = 500
"""Length of article content to include in RAG context previews"""


# ============================================
# Article Structure Constants
# ============================================
H1_PATTERN = r'^#\s+.+$'
"""Regex pattern for matching H1 headings in markdown"""

H2_PATTERN = r'^##\s+(.+)$'
"""Regex pattern for matching and extracting H2 headings"""

H2_H3_PATTERN = r'^#{2,3}\s+.+$'
"""Regex pattern for matching H2 and H3 headings"""

MIN_HEADING_COUNT = 3
"""Minimum number of H2/H3 headings expected in a well-structured article"""


# ============================================
# Validation Constants
# ============================================
PLACEHOLDER_KEYWORDS = ["[Insert", "[Add", "[TODO", "lorem ipsum"]
"""Common placeholder text patterns to detect in generated content"""


# ============================================
# Qdrant Connection Constants
# ============================================
QDRANT_MAX_RETRIES = 5
"""Maximum number of connection retry attempts for Qdrant"""

QDRANT_INITIAL_RETRY_DELAY = 2
"""Initial retry delay in seconds (uses exponential backoff)"""


# ============================================
# API Timeout Constants
# ============================================
METADATA_EXTRACTION_CONTENT_LIMIT = 3000
"""Maximum content length to send for metadata extraction (avoid token limits)"""


# ============================================
# Service Health Check Messages
# ============================================
HEALTH_STATUS_HEALTHY = "healthy"
HEALTH_STATUS_UNHEALTHY = "unhealthy"
HEALTH_STATUS_DEGRADED = "degraded"
HEALTH_STATUS_OPERATIONAL = "operational"


# ============================================
# HTTP Status Messages
# ============================================
ERROR_TYPE_VALIDATION = "ValidationError"
ERROR_TYPE_INTERNAL = "InternalServerError"
ERROR_TYPE_NETWORK = "NetworkError"
ERROR_TYPE_UNKNOWN = "UnknownError"
