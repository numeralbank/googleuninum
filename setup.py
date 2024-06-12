from setuptools import setup
import json


with open("metadata.json") as fp:
    metadata = json.load(fp)


setup(
    name="lexibank_googleuninum",
    description=metadata["title"],
    license=metadata.get("license", ""),
    url=metadata.get("url", ""),
    py_modules=["lexibank_googleuninum"],
    include_package_data=True,
    zip_safe=False,
    entry_points={"lexibank.dataset": ["googleuninum=lexibank_googleuninum:Dataset"]},
    install_requires=["pylexibank>=3.0"],
    extras_require={"test": ["pytest-cldf"]},
)
