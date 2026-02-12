"""
Setup configuration for AI Communication Engine
Enables package installation and distribution
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="ai-communication-engine",
    version="1.0.0",
    description="Real-time intelligence middleware for VoIP & walkie-talkie systems",
    long_description=long_description,
    long_description_content_type="text/markdown",
    
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourname/ai-communication-engine",
    
    license="MIT",
    
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Communications :: Telephony",
        "Topic :: Software Development :: Libraries",
    ],
    
    keywords=[
        "voip",
        "communication",
        "transcription",
        "intent-classification",
        "task-management",
        "notifications",
        "walkie-talkie",
        "ai",
        "nlp"
    ],
    
    packages=find_packages(include=["*"]),
    
    python_requires=">=3.12",
    
    install_requires=[
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0",
        "pydantic==2.4.2",
        "pydantic-settings==2.0.3",
        "sqlalchemy==2.0.23",
        "alembic==1.12.1",
        "aiofiles==23.2.1",
        "openai==1.0.0",
        "SpeechRecognition==3.10.0",
        "pydub==0.25.1",
        "requests==2.31.0",
        "twilio==8.10.0",
        "vonage==3.1.0",
        "firebase-admin==6.2.0",
        "python-dotenv==1.0.0",
        "python-multipart==0.0.6",
        "python-jose[cryptography]==3.3.0",
        "loguru==0.7.2",
        "numpy>=1.26.0",
        "librosa==0.10.0",
        "redis==5.0.1",
    ],
    
    extras_require={
        "dev": [
            "pytest==7.4.3",
            "pytest-asyncio==0.21.1",
            "black==23.11.0",
            "flake8==6.1.0",
            "mypy==1.7.0",
            "pre-commit==3.5.0",
        ],
        "database": [
            "psycopg2-binary==2.9.9",  # PostgreSQL adapter
            "pymongo==4.6.0",           # MongoDB adapter
        ],
        "monitoring": [
            "prometheus-client==0.19.0",
            "opentelemetry-api==1.21.0",
            "opentelemetry-sdk==1.21.0",
        ],
        "docs": [
            "sphinx==7.2.6",
            "sphinx-rtd-theme==2.0.0",
        ]
    },
    
    entry_points={
        "console_scripts": [
            "ai-engine=AI-CommunicationEngine:main",
        ],
    },
    
    project_urls={
        "Bug Tracker": "https://github.com/yourname/ai-communication-engine/issues",
        "Documentation": "https://github.com/yourname/ai-communication-engine/wiki",
        "Source Code": "https://github.com/yourname/ai-communication-engine",
    },
)
