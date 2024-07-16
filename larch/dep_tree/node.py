import re
import sys
from typing import List

from colorama import Fore

from larch.database.find_seed import find_seed
from larch.database.local import get_all_installed_pkg_str
from larch.sandbox.safe_exec import safe_exec_seed


class Node:
    class NodeType:
        INSTALLED = 0
        REMOTE = 1
        UNINSTALLING = 2

    parents = []
    children = []

    all_nodes = []
    node_type: NodeType = None

    name = ""
    ver = ""

    def __init__(self, parents, children, pkg_str):
        self.parents = parents
        self.children = children

        pkg_str = re.sub(r"\s*", "", pkg_str)
        self.pkg_str = pkg_str

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
        self.comparator = pkg_ver[0] if (pkg_ver and pkg_ver[0]) else None

        if self.ver and not self.comparator:
            self.comparator = "=="
        # endregion

        # region Get children
        deps = None

        if self.name not in ("@user", "@local"):
            seed_instance = find_seed(self.name, self.comparator, self.ver)

            if seed_instance is None:
                ver_info = ""

                if self.comparator and self.ver:
                    ver_info = self.comparator + self.ver

                print(
                    Fore.RED
                    + f"The following package does not exist: '{self.name}{ver_info}'. Stopping"
                )

                sys.exit(1)

            self.seed_code = seed_instance.seed_code

            self.node_type = (
                Node.NodeType.INSTALLED
                if seed_instance.seed_type == seed_instance.FoundSeedType.INSTALLED
                else Node.NodeType.REMOTE
            )

            loc = safe_exec_seed(self.seed_code)
            deps = loc.get("DEPENDENCIES", None)

        for child in self.children:
            child.parents.append(self)

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

        return f"Node(name = '{self.name}', version = '{ver}', type = {self.node_type}, parents = {self.parents})"

    def __repr__(self) -> str:
        return self.__str__()

    @staticmethod
    def reset():
        Node.all_nodes = []

    def shake_tree():
        def merge_nodes(nodes: List[Node]) -> Node:
            if len(nodes) == 1:
                return nodes[0]

            if len(nodes) == 0:
                raise Exception("No nodes to merge")

            merged_node = nodes[0]

            for node in nodes[1:]:
                merged_node.parents = [*merged_node.parents, *node.parents]

                if set([Node.NodeType.INSTALLED, Node.NodeType.REMOTE]) == set(
                    [merged_node.node_type, node.node_type]
                ):
                    merged_node.node_type = Node.NodeType.INSTALLED

                if node.ver and not merged_node.ver:
                    merged_node.ver = node.ver
                    merged_node.comparator = "=="

                if node.ver and merged_node.ver and node.ver != merged_node.ver:
                    raise Exception(
                        "Unresolved dependency conflict: "
                        + f"{node.name}{node.comparator}{node.ver} and "
                        + f"{merged_node.name}{merged_node.comparator}{merged_node.ver}"
                    )  # TODO

            return merged_node

        package_str_to_nodes = {}

        for node in Node.all_nodes:
            package_str = node.name

            if package_str in package_str_to_nodes:
                package_str_to_nodes[package_str].append(node)
            else:
                package_str_to_nodes[package_str] = [node]

        new_node_list = []

        for _, nodes in package_str_to_nodes.items():
            new_node_list.append(merge_nodes(nodes))

        Node.all_nodes = new_node_list

        return Node.all_nodes


Node(
    [], list(Node([], [], pkg_str) for pkg_str in get_all_installed_pkg_str()), "@local"
)
