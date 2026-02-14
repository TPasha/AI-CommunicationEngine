#!/usr/bin/env python3
"""Organize project files into proper folder structure."""
import os
import shutil
from pathlib import Path

root = Path(r'd:\AI Communication Engine')
os.chdir(root)

# File mappings: source -> destination folder
moves = {
    # Docs
    'ARCHITECTURE.md': 'docs',
    'MISSION_CONTROL_GUIDE.md': 'docs',
    'QUICKSTART.md': 'docs',
    'QUICK_REFERENCE.md': 'docs',
    'RUNNING_AND_TESTING.md': 'docs',
    'STATUS.md': 'docs',
    'TECHNICAL_IMPLEMENTATION.md': 'docs',
    'API_REFERENCE.md': 'docs',
    
    # Config
    'config.ini': 'config',
    
    # Core source
    'AI-CommunicationEngine.py': 'src',
    'intent_classifier.py': 'src',
    'models.py': 'src',
    'notification_service.py': 'src',
    'task_action_engine.py': 'src',
    'transcription_service.py': 'src',
    'webhook_handlers.py': 'src',
    
    # Tests
    'test_dashboard.py': 'tests',
    'test_integration.py': 'tests',
    'test_root.py': 'tests',
    'test_quick.ps1': 'tests',
    
    # Docker
    'Dockerfile': 'docker',
    'docker-compose.yml': 'docker',
    'docker-compose.mvp.yml': 'docker',
    
    # Scripts/utils
    'fix_jsx.py': 'scripts',
    'demo.py': 'mvp',
}

moved = []
failed = []

for source, dest_folder in moves.items():
    src_path = root / source
    dest_path = root / dest_folder / source
    
    if src_path.exists():
        try:
            shutil.move(str(src_path), str(dest_path))
            moved.append(f"{source} → {dest_folder}/")
        except Exception as e:
            failed.append(f"{source}: {e}")
    else:
        failed.append(f"{source}: not found")

print("=" * 60)
print("PROJECT REORGANIZATION COMPLETE")
print("=" * 60)
print(f"\nMoved: {len(moved)} files")
for m in moved:
    print(f"  ✓ {m}")

if failed:
    print(f"\nFailed: {len(failed)} files")
    for f in failed:
        print(f"  ✗ {f}")

print("\n" + "=" * 60)
print("New structure:")
print("=" * 60)
for folder in ['src', 'tests', 'docs', 'config', 'docker', 'mvp', 'scripts']:
    folder_path = root / folder
    if folder_path.exists():
        files = list(folder_path.glob('*'))
        if files:
            print(f"\n{folder}/")
            for f in sorted(files)[:5]:
                print(f"  - {f.name}")
            if len(files) > 5:
                print(f"  ... and {len(files) - 5} more")
