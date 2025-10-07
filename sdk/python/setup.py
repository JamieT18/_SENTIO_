"""Setup file for Sentio Python SDK"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sentio-sdk",
    version="2.0.0",
    author="Sentio Development Team",
    description="Official Python SDK for Sentio 2.0 Trading API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JamieT18/Sentio-2.0",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.9",
            "mypy>=0.900",
        ],
    },
    keywords="trading api sdk sentio stocks finance",
    project_urls={
        "Bug Reports": "https://github.com/JamieT18/Sentio-2.0/issues",
        "Source": "https://github.com/JamieT18/Sentio-2.0",
        "Documentation": "https://github.com/JamieT18/Sentio-2.0/blob/main/API.md",
    },
)
