import setuptools

with open('README.md') as f:
    long_description = f.read()

setuptools.setup(
    name="WSTrade-alhparsa",  # Replace with your own username
    version="0.0.1a1",
    author="Parsa Alamzadeh",
    author_email="alh.parsa@gmail.com",
    description="A wrapper for WS Trade API to remotely execute orders",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alhparsa/wstrade-python-wrapper-api",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
