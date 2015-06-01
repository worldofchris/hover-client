from setuptools import setup

setup(
    name="hover-client",
    version="0.1",
    description="Python client for the undocumented, unofficial Hover.com API.",
    author="Chris Young - based on work by Dan Krause",
    license="LICENSE.md",
    author_email="chris@chrisyoung.org",
    platforms=["Any"],
    packages=["hover"],
    include_package_data=True,
    install_requires=[
        "mock==1.0.1",
        "nose==1.3.6",
        "requests==2.7.0"
    ]
)
