from setuptools import setup, find_packages

with open('requirements.txt', encoding="utf-8-sig") as f:
    requirements = f.readlines()
with open('README.md', encoding='utf-8') as f:
    long_description = f.read()
setup(
    name="weather-retriever",
    version="0.1.0",
    author="KimRass",
    author_email="purflow64@gmail.com",
    description="Natural Language Weather Retriever",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/KimRass/weather-retriever",
    packages=find_packages(where="src"),
    install_requires=requirements,
)
