import dnf
import os
import shutil

from jinja2 import Template

from packaging import version

from tools.logger import logger
from tools import CACHE_PATH, REPO_PATH
from tools import SLICE_PATH, EP_SPLITTER_PATH


class Progress(dnf.callback.DownloadProgress):
    """Custom download progress callback"""

    def __init__(self):
        self.last_percent = {}

    def start(self, total_files, total_size):
        logger.info(f"Download started: "
                    f"{total_files} files, "
                    f"total size {total_size / 1024 / 1024:.2f} MB")

    def progress(self, payload, done):
        name = str(payload)
        total = payload.download_size

        if total == 0:
            percent = 100
        else:
            percent = int(done / total * 100)

        last = self.last_percent.get(name, -1)

        if percent == 100 or percent - last >= 5:
            if percent == last:
                return
            logger.info(f"Downloading: {name} [{percent}%]")
            self.last_percent[name] = percent

    def end(self, payload, status, msg):
        pass

def init_dnf_client(arch: str, release: str, output: str) -> dnf.Base:
    """
    Initialize the DNF Base object and configure repositories.

    return:
        Configured dnf.Base object
    """
    try:
        dnf_client = dnf.Base()
        conf = dnf_client.conf
        conf.destdir = output
        conf.arch = arch
        conf.basearch = arch
        conf.substitutions["basearch"] = arch

        # Initialize the repository using the openEuler.template.
        conf.reposdir = init_dnf_repo(arch, release)
        if not os.path.exists(CACHE_PATH):
            os.makedirs(CACHE_PATH)
        conf.cachedir = CACHE_PATH

        dnf_client.read_all_repos()
        dnf_client.fill_sack()
        return dnf_client
    except Exception as e:
        logger.error(f"Failed to client DNF API client: {e}")
        raise e


def init_dnf_repo(arch: str, release: str,) -> str:
    repo_dir = os.path.join(REPO_PATH, release)
    if not os.path.exists(repo_dir):
        os.makedirs(repo_dir)
    repo_file = os.path.join(repo_dir, "openEuler.repo")
    params = {"release": release, "basearch": arch}

    template_file = os.path.join(
        SLICE_PATH,
        "repo",
        "openEuler.template"
    )
    with open(template_file, "r", encoding="utf-8") as f:
        repo_config = f.read()
    repo_template = Template(repo_config)
    repo_text = repo_template.render(params)
    with open(repo_file, "w", encoding="utf-8") as f:
        f.write(repo_text)
    return os.path.dirname(repo_file)


def download(dnf_client: dnf.Base, package: str) -> str:
    """
    Download the package using the specified release and arch.

    return:
        Local package path (absolute path) to the downloaded package
    """

    # download openEuler rpms by `openEuler.repo`
    try:
        query = dnf_client.sack.query()
        packages = query.available().filter(name=package)
        if not packages:
            logger.error(f"Not found package: {package}!")
            return ""

        # select the latest released package version
        latest_package = max(
            packages,
            key=lambda p: (version.parse(p.version), p.release)
        )
        logger.debug(f"Downloading package: {latest_package}...")
        # download
        dnf_client.download_packages([latest_package], progress=Progress())
    except Exception as e:
        logger.error(
            f"Unexpected error while downloading {package}: {e}"
        )
        raise e

    local_pkg = latest_package.localPkg()
    if not local_pkg:
        raise RuntimeError(
            f"Failed to download: {package}!"
        )
    return local_pkg


def clear(base: dnf.Base) -> None:
    if base:
        base.close()
    if os.path.exists(CACHE_PATH):
        shutil.rmtree(CACHE_PATH)
    if os.path.exists(REPO_PATH):
        shutil.rmtree(REPO_PATH)
    if os.path.exists(SLICE_PATH):
        shutil.rmtree(SLICE_PATH)
    if os.path.exists(EP_SPLITTER_PATH):
        shutil.rmtree(EP_SPLITTER_PATH)
