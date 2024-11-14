from setuptools import setup, Extension, find_packages
from Cython.Build import cythonize
import numpy
import os
import platform

# Determine platform-specific settings
system = platform.system()
libraries = []
library_dirs = []
include_dirs = [numpy.get_include(), os.path.abspath("src")]
extra_compile_args = ["-fPIC"]  # Position-independent code
extra_link_args = []
define_macros = []

if system == "Darwin":  # macOS
    # Link against SBIGUDrv framework
    extra_link_args.extend(["-framework", "SBIGUDrv", "-F/Library/Frameworks"])
elif system == "Linux":
    # Link against libsbigudrv
    libraries.append("sbigudrv")
elif system == "Windows":
    # Link against SBIGUDrv.lib in src directory
    libraries.append("SBIGUDrv")
    library_dirs.append(os.path.abspath("src"))
    include_dirs.append(os.path.abspath("src"))
else:
    raise RuntimeError(f"Unsupported platform: {system}")

# Handle cfitsio
INCLUDE_CFITSIO = os.environ.get("INCLUDE_CFITSIO", "0") == "1"
if INCLUDE_CFITSIO:
    libraries.append("cfitsio")
    if system == "Windows":
        # Adjust these paths to where cfitsio is installed on Windows
        include_dirs.append("path_to_cfitsio_include")
        library_dirs.append("path_to_cfitsio_lib")
    else:
        include_dirs.append("/usr/include/cfitsio")
    define_macros.append(("INCLUDE_FITSIO", "1"))
else:
    define_macros.append(("INCLUDE_FITSIO", "0"))

# Define the Cython extension
extensions = [
    Extension(
        "pyobs_sbig.sbigudrv",
        sources=["pyobs_sbig/sbigudrv.pyx", "src/csbigcam.cpp", "src/csbigimg.cpp"],
        libraries=libraries,
        library_dirs=library_dirs,
        include_dirs=include_dirs,
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
        define_macros=define_macros,
        language="c++",
    )
]

# Setup configuration
setup(
    name="pyobs-sbig",
    version="1.0.7",
    description="pyobs module for SBIG cameras",
    author="Tim-Oliver Husser",
    author_email="thusser@uni-goettingen.de",
    license="MIT",
    packages=find_packages(),
    ext_modules=cythonize(
        extensions,
        compiler_directives={"binding": True, "language_level": "3"},
    ),
    include_dirs=[numpy.get_include()],
    install_requires=[
        "numpy>=1.25.1",
        "astropy>=5.3.1",
        "pyobs-core>=1.4.5",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.9,<3.13",
    # pip install .[dev]
    extras_require={
        "dev": [
            "black>=23.7.0",
            "pre-commit>=3.3.3",
            "sphinx-rtd-theme>=1.0",
            "Sphinx>=4.4",
            "Cython>=3.0.0",
        ],
    },
)
