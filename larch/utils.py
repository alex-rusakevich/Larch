indentaion_level = 0
indentaion = "  "


def set_print_indentaion_lvl(int_lvl: int):
    global indentaion_level
    indentaion_level = int_lvl


def sp_print(*args, **kwargs):
    global indentaion_level

    if kwargs.pop("no_indentation", False) is False:
        print(indentaion * indentaion_level, end="")

    print(*args, **kwargs)
