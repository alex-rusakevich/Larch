HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9,it;q=0.8,es;q=0.7",
    "Accept-Encoding": "identity",
    "Referer": "https://google.com/",
}

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


def str_to_version_tuple(ver: str) -> tuple:
    result = []

    for i in ver.split("."):
        if i.isdigit():
            result.append(int(i))
        else:
            result.append(i)

    return tuple(result)
