import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="prjxray",
    version="0.0.1",
    author="SymbiFlow Authors",
    author_email="symbiflow@lists.librecores.org",
    description="Project X-Ray libraries",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SymbiFlow/prjxray",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: ISC License",
        "Operating System :: OS Independent",
    ],
)
