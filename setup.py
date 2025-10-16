"""Setuptools configuration for Calliope."""

from __future__ import annotations

from pathlib import Path

from setuptools import find_packages, setup


def load_readme() -> str:
    readme_path = Path(__file__).parent / "README.md"
    return readme_path.read_text(encoding="utf-8")


setup(
    name="calliope",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "gitpython>=3.1.0",
        "openai>=1.0.0",
        "anthropic>=0.18.0",
        "click>=8.0.0",
        "rich>=13.0.0",
        "pyyaml>=6.0",
        "python-dotenv>=1.0.0",
        "python-docx>=1.0.0",
        "markdown>=3.4.0",
    ],
    entry_points={
        "console_scripts": [
            "calliope=calliope.cli:main",
        ],
    },
    author="Your Name",
    description="Git-based version control for fiction writers with AI",
    long_description=load_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/calliope",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)
