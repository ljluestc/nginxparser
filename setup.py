#!/usr/bin/env python
"""Setup script for nginxparser"""

from setuptools import setup

# Read the README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="nginxparser",
    version="2.0.0",
    description="Comprehensive nginx configuration parser with enhanced features",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="JoyChou93",
    url="https://github.com/JoyChou93/nginxparser",
    py_modules=["nginx"],
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
    ],
    keywords="nginx parser configuration config parse",
    entry_points={
        "console_scripts": [
            "nginxparser=nginx:main",
        ],
    },
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "coverage>=7.0.0",
            "flake8>=6.0.0",
            "pylint>=2.17.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.0.0",
            "bandit>=1.7.0",
            "pre-commit>=3.0.0",
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "coverage>=7.0.0",
        ],
    },
)
