from setuptools import find_packages, setup

with open('README.md') as readme_file:
    README = readme_file.read()

with open('LICENSE.md') as license_file:
    LICENSE = license_file.read()

setup(
    name='acstools',
    version='0.1.0',
    description='Tools for appending Census data to a given address',
    long_description=README,
    long_description_content_type="text/markdown",
    author='Michael Bryan',
    author_email="<michael.bryan@openenvironments>",
    packages=find_packages(),
    install_requires=['datetime','json','pandas','requests','sys'],  
    license=LICENSE
)

