NAME = "antconc3"
VERSION = (3, 5, 9)
ARCH = ("Windows_64bit",)
DESCRIPTION = "A freeware corpus analysis toolkit for arrying out corpus linguistics research and data-driven learning"

AUTHOR = "Laurence Anthony (https://laurenceanthony.net)"
MAINTAINER = "Alexander Rusakevich (mr.alexander.rusakevich@gmail.com)"
URL = "https://laurenceanthony.net/software/antconc/"
LICENSE = "https://laurenceanthony.net/software/antconc/releases/AntConc424/license.pdf"

SOURCE = {
    "antconc.exe": "https://laurenceanthony.net/software/antconc/releases/AntConc359/AntConc_64bit.exe"
}


def install(temp_dir: str, dest_dir: str):
    copyfile(join_path(temp_dir, "antconc.exe"), dest_dir)
    return "antconc.exe"
