import pathlib
import re
import subprocess
import sys
import traceback
import pkg_resources


def install_package(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    except subprocess.CalledProcessError as e:
        print(f"Error installing package {package}: {e}", file=sys.stderr)
        return False
    return True


def is_package_installed(package_name, comparison=None, required_version=None):
    try:
        installed_version = pkg_resources.get_distribution(package_name).version
        if comparison and required_version:
            return eval(f'"{installed_version}" {comparison}= "{required_version}"')
        return True
    except:
        return False


def main():
    req_file = pathlib.Path(__file__).resolve().parent / "requirements.txt"
    req_re = re.compile(r'^([^=<>~]*)\s*(?:([=<>~])=\s*([^=<>~]*))?$')

    with open(req_file) as file:
        for package in file:
            package = package.strip()
            match = req_re.match(package)
            if not match:
                print(f"Invalid package format: {package}", file=sys.stderr)
                continue

            package_name, comparison, required_version = match.groups()
            if not is_package_installed(package_name, comparison, required_version):
                install_package(package)


main()
