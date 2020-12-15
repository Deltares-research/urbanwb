from setuptools import setup

setup(
    name="urbanwb",
    version="0.2.0",
    description="Urban Water Balance",
    long_description="",
    url="https://gitlab.com/deltares/urban/urbanwb",
    author="Wenxing Zhang",
    author_email="w.x.zhang93@gmail.com",
    license="MIT",
    packages=["urbanwb"],
    test_suite="tests",
    python_requires=">=3.6",
    install_requires=["numpy", "pandas", "toml", "fire", "tqdm", "matplotlib", "tabulate"],
    extras_require={
        "dev": ["black", "pytest", "pytest-cov", "sphinx", "sphinx_rtd_theme"]
    },
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
