"""
Advanced Camera Array Tool for Cinema 4D
A comprehensive plugin for creating camera arrays for 3D visualization and photogrammetry
"""

# Plugin initialization
import c4d
import os
import sys

# Add plugin directory to path
plugin_dir = os.path.dirname(__file__)
if plugin_dir not in sys.path:
    sys.path.insert(0, plugin_dir)

# Import main plugin
from camera_to_take import main

# Register plugin
if __name__ == '__main__':
    main()