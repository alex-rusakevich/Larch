import sys

from colorama import Fore
from sqlalchemy import select
from tabulate import tabulate

from larch.database.local import LocalPackage
from larch.database.local import local_db_conn as loccon
from larch.database.remote import RemotePkgMeta
from larch.database.remote import remote_db_conn as remcon


def list_packages(list_installed=False, list_catalog=False):
    if list_installed and list_catalog:
        print(Fore.RED + "Only one type of list can be shown in single run")
        sys.exit(1)

    if list_installed:
        inst_list = loccon.execute(select(LocalPackage).order_by("name"))

        if inst_list == []:
            print("No packages installed yet")
        else:
            for pkg in inst_list:
                pkg_name = pkg.name
                pkg_ver = pkg.version

                print(f"{pkg_name}=={pkg_ver}")
    elif list_catalog:
        catalog_packages = remcon.execute(select(RemotePkgMeta).order_by("name"))
        print(
            tabulate(
                ((row[1], row[2].replace("\n", " ")) for row in catalog_packages),
                headers=["Name", "Description"],
                tablefmt="github",
            )
        )
    else:
        print(
            Fore.RED + "Package list type hasn't been specified, please, consult --help"
        )
        sys.exit(1)
