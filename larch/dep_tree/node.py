import re
import sys

from colorama import Fore

from larch.database.find_seed import find_seed
from larch.sandbox.safe_exec import safe_exec_seed


class Node:
    class NodeType:
        INSTALLED = 0
        REMOTE = 1

    parents = []
    children = []

    all_nodes = []
    node_type: NodeType = None

    name = ""
    ver = ""

    def __init__(self, parents, children, pkg_str):
        self.parents = parents
        self.children = children

        # region Parse version
        self.name = re.sub(r"(>=|==|!=|<=|<|>).*", "", pkg_str).strip()

        pkg_ver = re.search(r"(>=|==|!=|<=|<|>)(.*)", pkg_str)
        if pkg_ver:
            pkg_ver = (pkg_ver.group(1), pkg_ver.group(2).strip())

        if type(pkg_ver) in (list, tuple):
            if not pkg_ver[0] or not pkg_ver[1]:
                print(Fore.RED + f"Wrong version format: '{pkg_str}', stopping")
                sys.exit(1)

        self.ver = pkg_ver[1] if pkg_ver else None
        self.comparator = pkg_ver[0] if pkg_ver else None
        # endregion

        # region Get children
        deps = None

        if self.name != "@root":
            seed_instance = find_seed(self.name, self.comparator, self.ver)
            seed_code = seed_instance.seed_code

            self.node_type = (
                Node.NodeType.INSTALLED
                if seed_instance.seed_type == seed_instance.FoundSeedType.INSTALLED
                else Node.NodeType.REMOTE
            )

            loc = safe_exec_seed(seed_code)
            deps = loc.get("DEPENDENCIES", None)

        if deps:
            for dep in deps:
                self.children.append(Node([self], [], dep))
        # endregion

        Node.all_nodes.append(self)

    def __str__(self):
        if not self.ver:
            ver = None
        else:
            ver = f"{self.comparator}{self.ver}"

        return f"Node(name = {self.name}, version = {ver}, children = {self.children})"

    def __repr__(self) -> str:
        return self.__str__()

    @staticmethod
    def reset():
        Node.all_nodes = []
