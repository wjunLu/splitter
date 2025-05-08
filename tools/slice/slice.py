import yaml

from typing import List, Any
from tools.slice.extra import SliceExtra, ExtraBuilder
from tools.logger import logger

SLICE_MANIFEST = "manifest"
SLCIE_CONTENTS = "contents"
SLICE_COMMON = "common"
SLICE_EXTRA = "extra"
SLICE_DEPS = "deps"


class Slice:
    name: str = None
    common: List[str] = None
    extra: SliceExtra = None
    deps: List[str] = None

    def __init__(self):
        self.name = ""
        self.common = []
        self.extra = SliceExtra()


class SliceBuilder:

    def __init__(self, data=None):
        if data is None:
            data = {}
        self.data = data
        self.slice = Slice()

    def set_name(self, slice_name: str):
        self.slice.name = slice_name
        return self

    def set_common(self):
        contents = self.data.get(SLCIE_CONTENTS, {})
        self.slice.common = contents.get(SLICE_COMMON, [])
        return self

    def set_extra(self):
        contents = self.data.get(SLCIE_CONTENTS, {})
        extra_obj = contents.get(SLICE_EXTRA, {})
        extra_builder = (
            ExtraBuilder(extra_obj)
            .set_text()
            .set_amd64()
            .set_arm64()
            .set_copy()
        )
        self.slice.extra = extra_builder.get_extra()
        return self

    def set_deps(self):
        deps = self.data.get(SLICE_DEPS, [])
        self.slice.deps = deps
        return self

    def get_slice(self):
        return self.slice


class SliceDefinitionFile:

    def __init__(self, file: str):
        self.filename = file
        self.deps = []
        self.slices = []
        self.package = ""
        self.data = {}

        # load SDF
        try:
            with open(file, "r", encoding="utf-8") as f:
                self.data = yaml.safe_load(f)
        except FileNotFoundError:
            logger.error(f"The file '{file}' was not found.")
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse '{file}'. {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")

        # get all elements
        self.parse()

    def parse(self):
        if not self.data:
            return
        try:
            # parse sdf yaml config to sdf object
            self.package = self.data.get("package", "")
            self.deps = self.data.get("deps", [])
            for slice_name, slice_data in self.data["slices"].items():
                if not slice_name:
                    continue
                builder = SliceBuilder(slice_data)
                slice = (
                    builder
                    .set_name(slice_name)
                    .set_extra()
                    .set_deps()
                    .set_common()
                    .get_slice()
                )
                self.slices.append(slice)
        except Exception as e:
            logger.error(
                f"Failed to parse slice definition file:"
                f" {self.filename}, {e}"
            )
            raise e
        return self

    def get_slices(self):
        return self.slices
