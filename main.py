import os

import RunHPL


def ls():
    return os.popen('dir').readlines()

print(ls())

# RunHPL.hpl()


