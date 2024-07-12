#!/usr/bin/env python
import argparse
import sys
import larch
import larch.install
import larch.update
import larch.upgrade


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

    subparsers = parser.add_subparsers(
        help="larch pkg manager commands", dest="command"
    )

    install_subparser = subparsers.add_parser(
        "install", help="install program using it's id or larchseed.py file"
    )
    install_subparser.add_argument(
        "-f",
        "--file",
        action="store_true",
        help="install larchseed.py file instead of using program's id",
    )
    install_subparser.add_argument("packages", nargs="+")

    subparsers.add_parser(
        "update", help="get newest packages' meta info from repository"
    )

    subparsers.add_parser(
        "upgrade", help="upgrade installed programs using local packages' meta info"
    )

    args = parser.parse_args()

    if args.version:
        print("v" + ".".join((str(i) for i in larch.__version__)))
        sys.exit(0)

    if args.command == "install":
        if args.file:
            larch.install.install_seeds(args.packages)
        else:
            larch.install.install_pkg_names(args.packages)
    elif args.command == "update":
        larch.update.update_pkg_meta()
    elif args.command == "upgrade":
        larch.upgrade.upgrade_installed_packages()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
