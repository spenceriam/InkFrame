#!/usr/bin/env python3
"""
Check the uploads directory for original photos
"""
import os

uploads_dir = "static/images/photos/uploads"

if os.path.exists(uploads_dir):
    print(f"Contents of {uploads_dir}:\n")
    
    files = os.listdir(uploads_dir)
    files.sort()
    
    for f in files:
        filepath = os.path.join(uploads_dir, f)
        size = os.path.getsize(filepath)
        print(f"{f:<40} {size:>10} bytes")
    
    print(f"\nTotal files: {len(files)}")
    
    # Count by type
    types = {}
    for f in files:
        ext = f.lower().split('.')[-1] if '.' in f else 'no_ext'
        types[ext] = types.get(ext, 0) + 1
    
    print("\nFiles by type:")
    for ext, count in sorted(types.items()):
        print(f"  .{ext}: {count} files")
else:
    print(f"Directory {uploads_dir} does not exist!")

# Also check thumbnails
thumbnails_dir = "static/images/photos/thumbnails"
if os.path.exists(thumbnails_dir):
    thumb_count = len(os.listdir(thumbnails_dir))
    print(f"\nThumbnails directory has {thumb_count} files")