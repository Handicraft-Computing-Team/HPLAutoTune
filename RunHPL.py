import os


def hpl():
    print("Running HPL...")
    os.popen('bsub < hpl.lsf')


def get_cpu_info(node_name):
    # 使用正则表达式写入节点名字
    command = 'bhost hg_' + node_name
    command += '>> ' + node_name + '.txt'
    os.system(command)
    print("Running CPU info...")


def compile_hpl():
    print("compiling HPL...")
    os.popen('bsub < compile.lsf')
