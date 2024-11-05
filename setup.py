from setuptools import setup, find_packages
from setuptools.command.install import install
from pathlib import Path
import shutil


class CustomInstallCommand(install):
    def run(self):
        # Call the standard install command first.
        super().run()

        city_coords_src = Path(__file__).resolve().parent/"weather_retriever/resources/city_coords.json"
        hidden_dir = Path.home()/".weather_retriever"
        city_coords_dst = hidden_dir/"city_coords.json"

        city_coords_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(str(city_coords_src), str(city_coords_dst))
        print(f"Copied '{city_coords_src}' to '{city_coords_dst}'")


def requirements():
    with open("requirements.txt", encoding="utf-8-sig") as f:
        requirements = f.readlines()
    return requirements


if __name__ == "__main__":
    setup(
        name="weather_retriever",
        version="0.1.13",
        packages=find_packages(),
        install_requires=requirements(),
        include_package_data=True,  # Include files specified in 'MANIFEST.in'.
        cmdclass={
            "install": CustomInstallCommand,
        },
        author="KimRass",
        author_email="purflow64@gmail.com",
        description="Natural Language Weather Retriever",
        long_description=open("README.md").read(),
        long_description_content_type="text/markdown",
        url="https://github.com/KimRass/weather_retriever",
        license="Apache License 2.0",
    )
