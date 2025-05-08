# coding=utf-8
import os
import shutil

PATHS = [
    os.path.join(os.path.dirname(os.__file__), "../../etc/splitter/"),
    "/usr/local/etc/splitter/",
    "/usr/etc/splitter/",
    "/etc/splitter/",
]

EP_SPLITTER_PATH = "/etc/splitter/"

for path in PATHS:
    if os.path.exists(path):
        EP_SPLITTER_PATH = path
        break

SLICE_REPO = "https://gitee.com/openeuler/slice-releases.git"
SLICE_PATH = os.path.join(EP_SPLITTER_PATH, "slice-releases")
SLICE_DIR = os.path.join(SLICE_PATH, "slices")
CACHE_PATH = os.path.join(EP_SPLITTER_PATH, "cache")
REPO_PATH = os.path.join(EP_SPLITTER_PATH, "repo")
SDF_DIR_PREFIX = os.path.join(EP_SPLITTER_PATH, "data")

if os.path.exists(CACHE_PATH):
    shutil.rmtree(CACHE_PATH)

if os.path.exists(REPO_PATH):
    shutil.rmtree(REPO_PATH)

if os.path.exists(SLICE_PATH):
    shutil.rmtree(SLICE_PATH)