import platform

from RestrictedPython import compile_restricted, safe_globals

from larch.passed_to_seed import copyfile, copytree, join_path, run_exe, unzip


def safe_exec_seed(code: str):
    loc = {}
    byte_code = compile_restricted(code, "<inline>", "exec")

    exec(
        byte_code,
        {
            **safe_globals,
            "join_path": join_path,
            "unzip": unzip,
            "copytree": copytree,
            "copyfile": copyfile,
            "run_exe": run_exe,
            "CURRENT_ARCH": platform.system() + "_" + platform.architecture()[0],
        },
        loc,
    )

    return loc
