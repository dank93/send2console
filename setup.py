import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="send2console",
    version="0.0.1",
    author="Daniel Kurek",
    author_email="dkurek93@gmail.com",
    description="Send code to a Jupyter console!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
)
