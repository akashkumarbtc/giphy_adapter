"""Setup configuration for giphy-adapter package."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip()
                    and not line.startswith("#")]

setup(
    name="giphy-adapter",
    version="1.0.0",
    author="Akash Kumar",
    author_email="akash.kumar.p.24@outlook.com",
    description="Production-ready async Python adapter for Giphy API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/akashkumarbtc/giphy_adapter.git",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.20.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.8.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ]
    },
    keywords="giphy api gif async aiohttp adapter",
    project_urls={
        "Bug Reports": "https://github.com/akashkumarbtc/giphy_adapter.git/issues",
        "Source": "https://github.com/akashkumarbtc/giphy_adapter.git",
        "Documentation": "https://github.com/akashkumarbtc/giphy_adapter.git#readme",
    },
)
