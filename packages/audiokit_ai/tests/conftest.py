# CONFIDENTIAL AND PROPRIETARY
# 
# Copyright (c) 2025 AudioKit.ai. All rights reserved.
# 
# This software is confidential and proprietary.
# 

# 
# This file is part of the AudioKit AI package.
# 

"""Pytest configuration file."""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
root_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(root_dir))

# Add the package directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
