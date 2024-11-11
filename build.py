import os
import shutil
import platform

from setuptools import Extension, Distribution
import numpy
from Cython.Build import cythonize
from Cython.Distutils.build_ext import new_build_ext as cython_build_ext


def build() -> None:
    # if running in RTD, skip compilation
    if os.environ.get("READTHEDOCS") == "True":
        return

    # Determine if cfitsio support is enabled
    INCLUDE_CFITSIO = os.environ.get("INCLUDE_CFITSIO", "0") == "1"

    # Platform-specific settings
    system = platform.system()
    extra_link_args = []
    libraries = []
    include_dirs = [numpy.get_include()]

    if system == "Darwin":  # macOS
        # Link against SBIGUDrv framework
        extra_link_args.extend(['-framework', 'SBIGUDrv', '-F/Library/Frameworks'])
    elif system == "Linux":
        # Link against libsbigudrv
        libraries.append('sbigudrv')
    else:
        raise RuntimeError(f"Unsupported platform: {system}")

    # Handle cfitsio
    if INCLUDE_CFITSIO:
        libraries.append('cfitsio')
        include_dirs.append('/usr/include/cfitsio')
        # Define a macro to include cfitsio in the code
        define_macros = [('INCLUDE_FITSIO', '1')]
    else:
        define_macros = [('INCLUDE_FITSIO', '0')]

    extensions = [
        Extension(
            "pyobs_sbig.sbigudrv",
            ["pyobs_sbig/sbigudrv.pyx", "src/csbigcam.cpp", "src/csbigimg.cpp"],
            libraries=libraries,
            extra_link_args=extra_link_args,
            include_dirs=include_dirs,
            extra_compile_args=["-fPIC"],
            define_macros=define_macros,
        )
    ]
    ext_modules = cythonize(
        extensions,
        compiler_directives={"binding": True, "language_level": "3"},
    )

    distribution = Distribution(
        {
            "name": "extended",
            "ext_modules": ext_modules,
            "cmdclass": {
                "build_ext": cython_build_ext,
            },
        }
    )

    distribution.run_command("build_ext")

    # copy to source
    build_ext_cmd = distribution.get_command_obj("build_ext")
    for ext in build_ext_cmd.extensions:
        filename = build_ext_cmd.get_ext_filename(ext.name)
        source_path = os.path.join(build_ext_cmd.build_lib, filename)
        dest_path = os.path.join(os.path.dirname(__file__), filename)
        dest_dir = os.path.dirname(dest_path)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        print(f"Copying {source_path} to {dest_path}")
        shutil.copyfile(source_path, dest_path)


if __name__ == "__main__":
    build()
