from setuptools import setup, find_packages
from setuptools.command.install import install
from pathlib import Path
import shutil


class CustomInstallCommand(install):
    def run(self):
        # Call the standard install command first.
        install.run(self)

        home_dir = Path.home()
        hidden_dir = home_dir/".weather-retriever"
        city_coords_src = Path(__file__).parent.resolve()/"resources/city_coords.json"
        city_coords_dst = hidden_dir/"city_coords.json"
        hidden_dir.mkdir(parents=True, exist_ok=True)

        shutil.copy(city_coords_src, city_coords_dst)
        print(f"Copied 'city_coords.json' to '{city_coords_dst}'")


def requirements():
    with open("requirements.txt", encoding="utf-8-sig") as f:
        requirements = f.readlines()
    return requirements


def readme():
    with open("README.md", encoding="utf-8-sig") as f:
        README = f.read()
    return README


if __name__ == "__main__":
    setup(
        name="weather-retriever",
        version="0.1.1",
        author="KimRass",
        author_email="purflow64@gmail.com",
        description="Natural Language Weather Retriever",
        long_description=readme(),
        long_description_content_type="text/markdown",
        url="https://github.com/KimRass/weather-retriever",
        packages=find_packages(where="weather-retriever"),
        install_requires=requirements(),
        include_package_data=True,  # Include files specified in 'MANIFEST.in'.
        cmdclass={
            "install": CustomInstallCommand,
        },
    )
