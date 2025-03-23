from setuptools import setup
import logging

# TODO
project_name="howlitbe"
requirements = list()
description="wat?"
author="What's your name"
long_description=""
url="example.com"

with open('requirements.txt', 'r') as f:
    # "Parse" requirements, exclude comments, and emptylines
    requirements = list(filter(lambda i: len(i) > 0 and not i.startswith('#'), f.readlines()))

print(f"requirements: {requirements}")

with open("README.md", 'r', encoding='utf-8') as f:
    long_description = f.read()


setup(
    name=project_name,
    packages=[
        "howlitbe",
        "howlitbe.scenario",
    ],
    package_data={
        "howlitbe": [
            "res/*.sh"
        ]
    },
    include_package_data=True,
    license="MIT",
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=url,
    author=author,
    setup_requires=["wheel"],
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8.0",
    version="0.0.1",
    entry_points=f"""
        [console_scripts]
        {project_name} = {project_name}.app:main
    """
)
