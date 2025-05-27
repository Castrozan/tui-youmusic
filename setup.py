from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="tui-youmusic",
    version="1.0.0",
    author="TUI YouTube Music Player",
    description="A beautiful Terminal User Interface for YouTube Music",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/tui-youmusic",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Sound/Audio :: Players",
        "Environment :: Console :: Curses",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "tui-youmusic=ytmusic_tui:main",
        ],
    },
    keywords="youtube music player tui terminal audio mpv",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/tui-youmusic/issues",
        "Source": "https://github.com/yourusername/tui-youmusic",
    },
) 