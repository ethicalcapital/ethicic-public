"""
Views package for public_site app.
"""

# Import all views from the main views.py file
import os
import sys

from public_site.views import *  # noqa: F401, F403, E402

# Add the parent directory to the path to import from views.py
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
