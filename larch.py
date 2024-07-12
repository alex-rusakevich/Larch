#!/usr/bin/env python
import argparse
import sys

import larch
import larch.install
import larch.run
import larch.uninstall
import larch.update
import larch.upgrade
from larch.installed_db import db_list_installed
from colorama import init


def main():
    init(autoreset=True)

    parser = argparse.ArgumentParser(
        description="MSLU repo's package management CLI tool"
    )
    parser.add_argument(
        "-v",
        "--version",
        action="store_true",
        help="show larch version and exit",
    )

    subparsers = parser.add_subparsers(
        help="larch pkg manager commands", dest="command"
    )

    # region Install command
    install_subparser = subparsers.add_parser(
        "install", help="install program using it's name or larchseed.py file"
    )
    install_subparser.add_argument(
        "-s",
        "--seed",
        action="store_true",
        help="install larchseed.py file instead of using program's name",
    )
    install_subparser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="ignore program exists or has lower version than installed",
    )
    install_subparser.add_argument("packages", nargs="+")
    # endregion

    uninstall_subparser = subparsers.add_parser(
        "uninstall", help="remove program using it's name"
    )
    uninstall_subparser.add_argument("packages", nargs="+")

    run_subparser = subparsers.add_parser("run", help="run program using it's name")
    run_subparser.add_argument("name")
    run_subparser.add_argument("args", nargs="*")
    run_subparser.add_argument(
        "-d",
        "--detached",
        action="store_true",
        help="run program and exit larch immediately",
    )

    subparsers.add_parser(
        "update", help="get newest packages' meta info from repository"
    )

    subparsers.add_parser(
        "upgrade", help="upgrade installed programs using local packages' meta info"
    )

    list_subparser = subparsers.add_parser(
        "list", help="get the list of packages and exit"
    )
    list_subparser.add_argument(
        "-i",
        "--installed",
        action="store_true",
        help="get list of locally installed packages",
    )

    args = parser.parse_args()

    if args.version:
        print(".".join((str(i) for i in larch.__version__)))
        sys.exit(0)

    if args.command == "install":
        if args.seed:
            larch.install.install_seeds(args.packages, args.force)
        else:
            larch.install.install_pkg_names(args.packages, args.force)
    elif args.command == "uninstall":
        larch.uninstall.uninstall_pkg_names(args.packages)
    elif args.command == "update":
        larch.update.update_pkg_meta()
    elif args.command == "upgrade":
        larch.upgrade.upgrade_installed_packages()
    elif args.command == "list":
        if args.installed:
            inst_list = db_list_installed()

            if inst_list == []:
                print("No packages installed yet")
            else:
                for pkg in inst_list:
                    pkg_name = pkg["name"]
                    pkg_ver = pkg["version"]

                    print(f"{pkg_name}=={pkg_ver}")
        else:
            print("Missing the list specificator (e.g. -i)")
    elif args.command == "run":
        larch.run.run_by_name(args.detached, args.name, args.args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
