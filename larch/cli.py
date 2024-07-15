import argparse
import sys

from colorama import init

import larch
import larch.commands.clear_cache
import larch.commands.install
import larch.commands.run
import larch.commands.uninstall
import larch.commands.update
import larch.commands.upgrade
from larch.commands.list import list_packages
from larch.utils import sp_print as print


def run_cli():
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
        "install", help="install package using it's name or larchseed.py file"
    )
    install_subparser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="ignore package exists or has lower version than installed",
    )
    install_subparser.add_argument("packages", nargs="+")
    # endregion

    uninstall_subparser = subparsers.add_parser(
        "uninstall", help="remove package using it's name"
    )
    uninstall_subparser.add_argument("packages", nargs="+")

    run_subparser = subparsers.add_parser("run", help="run package using it's name")
    run_subparser.add_argument("name")
    run_subparser.add_argument("args", nargs="*")
    run_subparser.add_argument(
        "-d",
        "--detached",
        action="store_true",
        help="run package and exit larch immediately",
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
        "upgrade", help="upgrade installed packages using local packages' meta info"
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
    list_subparser.add_argument(
        "-c",
        "--catalog",
        action="store_true",
        help="get list of programs which are present in the repository",
    )

    args = parser.parse_args()

    init(autoreset=True, strip=args.no_color)

    if args.version:
        print(".".join((str(i) for i in larch.__version__)))
        sys.exit(0)

    if args.command == "install":
        larch.commands.install.install_packages(args.packages, args.force)
    elif args.command == "uninstall":
        larch.commands.uninstall.uninstall_pkg_names(args.packages)
    elif args.command == "update":
        larch.commands.update.update_pkg_meta(args.force)
    elif args.command == "upgrade":
        larch.commands.upgrade.upgrade_installed_packages()
    elif args.command == "clear-cache":
        larch.commands.clear_cache.clear_cache()
    elif args.command == "list":
        list_packages(args.installed, args.catalog)
    elif args.command == "run":
        larch.commands.run.run_by_name(args.detached, args.name, args.args)
    else:
        parser.print_help()
