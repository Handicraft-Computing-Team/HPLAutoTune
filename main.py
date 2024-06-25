import os


def ls():
    return os.popen('ls').readlines()


