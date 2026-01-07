"""
Version information for InkFrame.

This module follows semantic versioning: MAJOR.MINOR.PATCH
- MAJOR: Breaking changes, API changes, architectural overhauls
- MINOR: New features, new components, significant enhancements (backwards compatible)
- PATCH: Bug fixes, typos, minor tweaks, performance improvements (backwards compatible)
"""

__version__ = "1.1.0"
__version_info__ = (1, 1, 0)

# Version metadata
VERSION_MAJOR = 1
VERSION_MINOR = 1
VERSION_PATCH = 0
VERSION_STRING = "1.1.0"
VERSION_FULL = f"InkFrame v{VERSION_STRING}"


def get_version():
    """Return the current version string."""
    return VERSION_STRING


def get_version_info():
    """Return the version as a tuple (major, minor, patch)."""
    return (VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH)


def get_full_version():
    """Return the full version string with product name."""
    return VERSION_FULL
