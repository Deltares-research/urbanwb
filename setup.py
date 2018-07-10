from setuptools import setup

setup(
    name="urbanwb",
    version="0.1.0",
    description="Urban Water Balance",
    long_description="",
    url="https://gitlab.com/wxzhang/UWM",
    author="Wenxing Zhang",
    author_email="w.x.zhang93@gmail.com",
    license="MIT",
    packages=["urbanwb"],
    test_suite="tests",
    python_requires=">=3.6",
    install_requires=["numpy", "pandas", "fire"],
    extras_require={"dev": ["sphinx"]},
    classifiers=[
        # https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    keywords="urban water balance modeling",
)
