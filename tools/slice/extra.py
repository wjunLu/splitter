import os
import shutil
from tools.parse import parse
from typing import List, Dict


EXTRA_TEXT = "text"
EXTRA_COPY = "copy"
EXTRA_ARM64 = "linux-aarch64"
EXTRA_AMD64 = "linux-x86_64"


class SliceExtra:

    def __init__(self):
        # <dst:src>
        self.arm64: List[str] = []
        self.amd64: List[str] = []
        self.copy: Dict[str, str] = {}
        self.text: Dict[str, str] = {}
        self.manifest: List[str] = []
        self.extra_files: List[str] = []

    def linux_arm64_handler(self, pkg_path: str, output: str):
        """
        Handle files specifically required for ARM architecture.
        """
        if not self.arm64:
            return self
        parse.extract_files(pkg_path, output, self.arm64)
        self.extra_files.extend(self.arm64)
        return self

    def linux_amd64_handler(self, pkg_path: str, output: str):
        """
        Handle files specifically required for AMD architecture.
        """
        if not self.amd64:
            return self
        parse.extract_files(pkg_path, output, self.amd64)
        self.extra_files.extend(self.amd64)
        return self

    def copy_handler(self, output: str):
        """
        Copy specified files to another location.
        """
        if not self.copy:
            return self
        for dst, src in self.copy:
            dst_path = os.path.join(output, dst)
            shutil.copy2(src, dst_path)
            self.extra_files.append(dst)
        return self

    def text_handler(self, output: str):
        """
        Copy specified text content to a target file.
        """
        if not self.text:
            return self

        for dst, text in self.text:
            dst_path = os.path.join(output, dst)
            with open(dst_path,  "w", encoding="utf-8") as f:
                f.write(text)
            self.extra_files.append(dst)
        return self

    # TODO waiting implement
    def manifest_handler(self, output: str):
        """
        Generate a `manifest.wall` file for CVE scanning.
        """
        return self


class ExtraBuilder:

    def __init__(self, data=None):
        if data is None:
            data = {}
        self.data = data
        self.extra = SliceExtra()

    def set_arm64(self):
        self.extra.arm64 = self.data.get(EXTRA_ARM64, [])
        return self

    def set_amd64(self):
        self.extra.amd64 = self.data.get(EXTRA_AMD64, [])
        return self

    def set_copy(self):
        self.extra.copy = self.data.get(EXTRA_COPY, {})
        return self

    def set_text(self):
        self.extra.text = self.data.get(EXTRA_TEXT, {})
        return self

    def get_extra(self):
        return self.extra
