#!/usr/bin/env python
import argparse
import sys

from colorama import init
from sqlalchemy import select

import larch
import larch.clear_cache
import larch.install
import larch.run
import larch.uninstall
import larch.update
import larch.upgrade
from larch.database.local import LocalPackage
from larch.database.local import local_db_conn as loccon


def main():
    parser = argparse.ArgumentParser(
        description="MSLU repo's package management CLI tool"
    )
    parser.add_argument(
        "-v",
        "--version",
        action="store_true",
        help="show larch version and exit",
    )
    parser.add_argument(
        "-n", "--no-color", action="store_true", help="disable colored output"
    )

    subparsers = parser.add_subparsers(
        help="larch pkg manager commands", dest="command"
    )

    # region Install command
    install_subparser = subparsers.add_parser(
        "install", help="install program using it's name or larchseed.py file"
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

    update_subparser = subparsers.add_parser(
        "update", help="get newest packages' meta info from repository"
    )
    update_subparser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="update remote.db no matter it exists or already up-to-date",
    )

    subparsers.add_parser(
        "upgrade", help="upgrade installed programs using local packages' meta info"
    )

    subparsers.add_parser("clear-cache", help="remove all cached downloads")

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

    init(autoreset=True, strip=args.no_color)

    if args.version:
        print(".".join((str(i) for i in larch.__version__)))
        sys.exit(0)

    if args.command == "install":
        larch.install.install_packages(args.packages, args.force)
    elif args.command == "uninstall":
        larch.uninstall.uninstall_pkg_names(args.packages)
    elif args.command == "update":
        larch.update.update_pkg_meta(args.force)
    elif args.command == "upgrade":
        larch.upgrade.upgrade_installed_packages()
    elif args.command == "clear-cache":
        larch.clear_cache.clear_cache()
    elif args.command == "list":
        if args.installed:
            inst_list = loccon.execute(select(LocalPackage).order_by("name"))

            if inst_list == []:
                print("No packages installed yet")
            else:
                for pkg in inst_list:
                    pkg_name = pkg.name
                    pkg_ver = pkg.version

                    print(f"{pkg_name}=={pkg_ver}")
        else:
            print("Missing the list specificator (e.g. -i)")
    elif args.command == "run":
        larch.run.run_by_name(args.detached, args.name, args.args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
