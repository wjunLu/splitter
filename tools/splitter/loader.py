import os

from typing import Set, Dict, Tuple, List, Optional
from tools.slice.extra import SliceExtra
from tools.slice.slice import SliceDefinitionFile
from tools.logger import logger
from tools import SLICE_DIR


def _parse_slice(slice: str) -> Tuple[str, str]:
    """
    Parse the SDF file name from slice name.
    """
    if "_" not in slice:
        raise ValueError(f"Invalid sdf name format: {slice}")
    info = slice.rsplit("_", 1)
    # Get the required {package}.yaml to generate the required slice
    pkgfile = f"{SLICE_DIR}/{info[0]}.yaml"
    slicename = info[1]
    return pkgfile, slicename


def load_cache(sdf_dir: str) -> Dict[str, SliceDefinitionFile]:
    """
    Load all the SDF.
    """
    sdf_cache = {}
    logger.debug(f"loading SDF files from {sdf_dir}:")
    for file in os.listdir(sdf_dir):
        logger.debug(file)
        if file.endswith(".yaml"):
            file = os.path.join(sdf_dir, file)
            sdf_obj = SliceDefinitionFile(file)
            sdf_cache[file] = sdf_obj
    return sdf_cache


class SplitterLoader:
    
    def __init__(self, sdf_dir: str, release: str):
        self.cached_pkgs = load_cache(sdf_dir)
        self.release = release

    def get_deps(self, slice: str, cached_deps: Optional[Set[str]]) -> Set[str]:
        """
        Recursively retrieve all dependencies for `slice`.

        args:
            cached_pkgs: The cached SDF data.
            slice: Name of the slice which requires to get its all deps.
            cached_deps: The cached dependencies, excludes those of `slice`.
        return: 
            All the dependencies for `slice`.
        """
        if cached_deps is None:
            cached_deps = set()

        if slice in cached_deps:
            return set()
        cached_deps.add(slice)

        required_pkg, required_slice = _parse_slice(slice)
        sdf_obj = self.cached_pkgs.get(required_pkg)
        if not sdf_obj:
            raise ValueError(f"Slice definition file: {required_pkg} is not found!")

        deps = set()
        # split required slice from its package
        for sc in sdf_obj.slices:
            if sc.name != required_slice:
                continue
            # `deps` in each first directory of SDF is required by its all `slices`
            if sc.deps:
                for item in sc.deps:
                    if "_" not in item:
                        continue
                    deps.add(item)
        for subdep in deps.copy():
            deps.update(
                self.get_deps(slice=subdep, cached_deps=cached_deps)
            )
        return deps

    def get_contents(self, slice: str) -> Tuple[str, List[str]]:
        """
        Retrieve contents of the current sdf dependency.

        args:
            slice: Name of the slice which requires to get its all common `contents`.
        return: 
            The dependent package name.
            Contents for `slice`.
        """
        common = []
        required_pkg, required_slice = _parse_slice(slice)
        sdf_obj = self.cached_pkgs.get(required_pkg)

        for slice in sdf_obj.slices:
            if slice.name != required_slice:
                continue
            if not slice.common:
                continue
            common = slice.common
        return sdf_obj.package, common

    def get_extras(self, slice: str) -> List[SliceExtra]:
        """
        Retrieve extra configs of the current sdf dependency.

        args:
            slice: Name of the slice which requires to get its `extra` items.
        return: 
            `extra` items for `slice`.
        """
        extras = []
        required_pkg, required_slice = _parse_slice(slice)
        sdf_obj = self.cached_pkgs.get(required_pkg)
        for sc in sdf_obj.slices:
            if sc.name != required_slice:
                continue
            if not sc.extra:
                continue
            extras.append(sc.extra)
        return extras

    def get_package(self, slice: str) -> str:
        """
        Retrieve package of the current sdf dependency.

        args:
            slice: Current sdf dependency.
        return: 
            Package of the current sdf dependency.
        """
        required_pkg, _ = _parse_slice(slice)
        sdf_obj = self.cached_pkgs.get(required_pkg)
        return sdf_obj.package
