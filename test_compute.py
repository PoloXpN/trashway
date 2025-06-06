#!/usr/bin/env python3
import sys
import os

# Add the dashboard app directory to the path
sys.path.append('dashboard/app')

try:
    from utils import compute_distances
    print("Successfully imported compute_distances")
    
    print("Testing compute_distances function...")
    compute_distances()
    print("compute_distances completed successfully!")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
