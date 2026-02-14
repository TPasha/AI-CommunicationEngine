#!/usr/bin/env python3
"""Test the root endpoint and check if HTML is correct."""
import subprocess
import sys

print("=" * 70)
print("TESTING ROOT ENDPOINT")
print("=" * 70)

try:
    # Get root endpoint response
    result = subprocess.run(
        [sys.executable, "-m", "urllib.request", "-c", """
import urllib.request
try:
    with urllib.request.urlopen('http://127.0.0.1:8800/', timeout=5) as resp:
        content = resp.read().decode('utf-8')
        print(f'Status: 200')
        print(f'Size: {len(content)} bytes')
        print(f'Has <html>: {"<html" in content}')
        print(f'Has <body>: {"<body" in content}')
        print(f'Has <div id="root">: {"<div id=\\"root\\"" in content}')
        print(f'Has AICommandCenter: {"AICommandCenter" in content}')
        print(f'Has unpkg.com/react: {"unpkg.com/react" in content}')
        print(f'Has unpkg.com/@babel: {"unpkg.com/@babel" in content}')
        print()
        print('First 300 chars:')
        print(content[:300])
except Exception as e:
    print(f'Error: {e}')
"""],
        capture_output=False
    )
except Exception as e:
    print(f"Failed to run test: {e}")
