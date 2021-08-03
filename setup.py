import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="swift-cloud-api",
    version="0.14.0",
    author="S.T.G. Fleuren",
    author_email="stijn.fleuren@swiftmobility.eu",
    description="Swift Mobility Cloud API Interface",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/stijnfleuren/SwiftCloudApi",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_data={'swift_cloud_py': ['examples/*.json']},
    include_package_data=True,
    install_requires=[
        'requests'
    ],
    python_requires='>=3.7',
)
