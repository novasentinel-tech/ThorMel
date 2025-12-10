from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="deepai-vulnerability-analyzer",
    version="1.0.0",
    author="DeepAI Security Team",
    author_email="team@deepai-security.edu",
    description="AI-powered vulnerability analysis system for cybersecurity research",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/novasentinel-tech/DeepAI",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Security",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    extras_require={
        "dev": ["pytest", "pytest-cov", "black", "flake8", "mypy"],
        "jupyter": ["jupyter", "jupyterlab"],
    },
    entry_points={
        "console_scripts": [
            "deepai-scan=scripts.run_single_scan:main",
            "deepai-train=scripts.train_ml_model:main",
        ],
    },
)
