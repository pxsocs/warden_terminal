from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

current_version = '0.0.0.2'

with open("version.txt", "w") as text_file:
    print(f"{current_version}", file=text_file)

reqs = ['ansi', 'urwid', 'emoji', 'tabulate', 'pyttsx3', 'yaspin']

setup(
    name="warden_terminal",
    version=current_version,
    author="Alpha Zeta",
    author_email="alphaazeta@protonmail.com",
    description="ANSI based text monitor for Bitcoin Info",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pxsocs/warden_terminal",
    include_package_data=True,
    packages=find_packages(),
    install_requires=reqs,
    setup_requires=reqs,
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    python_requires=">=3.6",
)
