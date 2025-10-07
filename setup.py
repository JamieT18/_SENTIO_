"""
Sentio: Intelligent Trading System
Setup configuration
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="sentio",
    version="2.0.0",
    author="Sentio Team",
    description="Intelligent Trading System with Multi-Strategy Engine and AI-Powered Decision Making",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JamieT18/Sentio-2.0",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",  # Config in config/.flake8
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "sentio=sentio.core.cli:main",
        ],
    },
)
