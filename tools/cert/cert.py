import subprocess
import os
from typing import Optional
from tools.logger import logger


DEFAULT_RPMDB_PATH="/var/lib/rpm"

def run_command(cmd: list, check: bool = True) -> bool:
    try:
        subprocess.run(cmd,
                       check=check, 
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {' '.join(cmd)}")
        logger.error(f"{e.stderr.decode().strip()}")
        return False
    except FileNotFoundError:
        logger.error(f"Command not found: {cmd[0]}")
        return False


def init_rpm_db(db_path: str) -> bool:
    logger.info("Initializing RPM database...")
    return run_command(["rpmdb", "--initdb", "--dbpath", db_path])


def add_package_to_db(db_path: str, rpm_file: str) -> bool:
    if not os.path.isfile(rpm_file):
        logger.error(f"RPM file not found: {rpm_file}")
        return False
    
    logger.info(f"Adding {rpm_file} to RPM database...")
    command = [
        "rpm",
        "-ivh",
        "--ignorearch",
        "--force",
        "--nodeps",
        "--justdb",
        "--dbpath", 
        db_path, 
        rpm_file
    ]
    return run_command(command)


def verify_package(db_path: str, pkg_name: str) -> Optional[str]:
    try:
        result = subprocess.run(
            ["rpm", "--dbpath", db_path, "-q", pkg_name],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None


class RPMCertPacker:
    """
    A class to pack RPM's installation information to support vulnerability scanning and SBOM.
    """
    def __init__(self, db_root: str):
        self.db_root = db_root
        self.db_path = db_root + DEFAULT_RPMDB_PATH
        if init_rpm_db(db_path=self.db_path):
            logger.info("Succeed to initalize RPM DB.")
        else:
            raise("Failed to initalize RPM DB.")

    def pack_cert(self, rpm_file: str) -> bool:
        if os.geteuid() != 0:
            raise("This script must be run as root!")
        if not add_package_to_db(db_path=self.db_path, rpm_file=rpm_file):
            return False
        pkg_name = os.path.basename(rpm_file).replace(".rpm", "").split("-")[0]
        pkg_info = verify_package(db_path=self.db_path, pkg_name=pkg_name)
        if not pkg_info:
            return False
        return True
