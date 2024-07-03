import os

import RunHPL


def ls():
    return os.popen('ls').readlines()

print(ls())

# RunHPL.hpl()


