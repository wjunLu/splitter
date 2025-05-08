import fnmatch
import os
import subprocess
import tempfile

from typing import List
from tools.logger import logger


def list_pkg_files(pkg_path: str) -> list[str]:
    """
    List all files in the RPM packages.

    Args:
        pkg_path (str): Path to the RPM package.

    Returns:
        list[str]: List of files in the RPM package.

    Raises:
        RuntimeError: If listing files fails.
    """
    try:
        rpm_process = subprocess.run(
            ["rpm2cpio", pkg_path],
            check=True,
            stdout=subprocess.PIPE
        )

        cpio_process = subprocess.run(
            ["cpio", "-t"],
            input=rpm_process.stdout,
            check=True,
            stdout=subprocess.PIPE
        )
        return cpio_process.stdout.decode().splitlines()
    except Exception as e:
        raise RuntimeError(f"Error listing files in RPM: {e}")


def match_files(file_list: List[str], patterns: List[str]) -> List[str]:
    """
    Filter files from a given list that match any of the specified patterns.

    args:
        file_list: List of RPM files.
        patterns: Pattern list to match.
    return: 
        List of matching files.
    """
    matched_files = []
    for file in file_list:
        for pattern in patterns:
            if fnmatch.fnmatch(file, pattern):
                matched_files.append(file)
                break
    return matched_files


def write_files(pkg_path: str, output_dir: str, matched_files: List[str]):
    """
    Extracts specific files from an RPM package.

    args:
        pkg_path: Rpm downloaded path.
        output_dir: Directory to save extracted files.
        matched_files: Set of file paths to extract from the downloaded RPM.
    """
    temp_file = None
    try:
        # Create a temporary file containing the list of files to extract
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp:
            tmp.write("\n".join(matched_files))
            temp_file = tmp.name
        logger.debug(f"Temporary file list created at: {temp_file}")

        # Run rpm2cpio and capture its output
        rpm_process = subprocess.run(
            ["rpm2cpio", pkg_path],
            check=True,
            stdout=subprocess.PIPE
        )

        # Run cpio with extracted file list to `output` directory
        subprocess.run(
            ["cpio", "-idmv", "-D", output_dir, "-E", temp_file],
            input=rpm_process.stdout,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"Failed to extract files from RPM '{pkg_path}': {e}"
        ) from e
    finally:
        # Ensure the temporary file is removed
        if temp_file and os.path.exists(temp_file):
            os.unlink(temp_file)


def extract_files(pkg_path: str, output_dir: str, patterns: List[str]):
    """
    Extract files from the RPM package.

    args:
        pkg_path: RPM package downloaded path.
        output_dir: Directory to save extracted files.
        patterns: List of file patterns to extract.
    """
    os.makedirs(output_dir, exist_ok=True)
    pkg_files = list_pkg_files(pkg_path)
    relative_patterns = list(map(
        lambda pattern: f".{pattern}", patterns
    ))
    matched_files = match_files(pkg_files, relative_patterns)
    write_files(pkg_path, output_dir, matched_files)
