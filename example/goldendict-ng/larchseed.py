PKG_NAME = "goldendict-ng"
PKG_VER = (6, 6, 3)
PKG_DESC = "The next generation GoldenDict (Supports Qt WebEngine & Qt6)"

AUTHOR = "@xiaoyifang (https://github.com/xiaoyifang)"
URL = "https://github.com/xiaoyifang/goldendict-ng"
LICENSE = "GPL3"

MAINTAINER = "Alexander Rusakevich (mr.alexander.rusakevich@gmail.com)"
SOURCE = {
    "goldendict.zip": "https://github.com/xiaoyifang/goldendict-ng/releases/download/v24.05.05-LiXia.ecd1138c/6.6.3-GoldenDict.exe_windows-2019_20240505.zip"
}


def install(temp_dir: str, dest_dir: str):
    unzip(join_path(temp_dir, "goldendict.zip"), temp_dir)
    copy(join_path(temp_dir, "GoldenDict-Windows.ecd1138c-142735"), dest_dir)
    return "GoldenDict.exe"
