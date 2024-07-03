import os


def io():
    print("Read")

    f = open("test.txt", "r")


def open_avail_lists():
    # queues
    os.system('bqueues >> queues.txt')
    file = open("queues.txt", "r")


def check_queue(node_name):
    os.popen('bhosts hg_ssc-cpu | grep ' + node_name)


# 定义要写入文件的内容
cpu_content = """
#!/bin/bash
#BSUB -q ssc-cpu ##队列名
#BSUB -J HPL-Test
#BSUB -n 1                  ##申请的 CPU 总核数
#BSUB -m b07u15a

hostfile=`echo $LSB_DJOB_HOSTFILE`
NP=`cat $hostfile | wc -l`

lscpu > cpu_info.txt
"""


def cpu_info(node_name):
    print("Getting cpu_info in node " + node_name)
    # 指定文件名
    file_name = 'cpu.lsf'

    # 打开文件并写入内容
    with open(file_name, 'w') as f:
        f.write(cpu_content)

    # 读取文件内容
    with open(file_name, 'r+') as f:
        file_contents = f.read()

    # 定位需要修改的行
    lines = file_contents.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('#BSUB -m'):
            lines[i] = f"#BSUB -m {node_name}"
            break  # 找到并修改后退出循环

    # 将修改后的内容写回文件
    updated_content = '\n'.join(lines)
    with open(file_name, 'w') as f:
        f.write(updated_content)

    print(f"find cpu info on node '{node_name}' with file '{file_name}'")

    os.popen(f"bsub < '{file_name}'")


def read_cpu_info():
    file_name = 'cpu.txt'
    try:
        # 打开文件并读取内容
        with open(file_name, 'r') as f:
            lines = f.readlines()

        # 查找包含 CPU(s) 的行并解析核心数
        for line in lines:
            if line.startswith('CPU(s):'):
                cpu_cores = int(line.split(':')[1].strip())
                print("CPU cores: ", cpu_cores)
                return cpu_cores

        # 如果没有找到 CPU(s) 行，默认返回 None 或者适合的错误处理
        return None

    except Exception as e:
        print(f"Error occurred while reading {file_name}: {str(e)}")
        return None


memory_size_content = """
#!/bin/bash
#BSUB -q ssc-cpu ##队列名
#BSUB -J HPL-Test
#BSUB -n 1                  ##申请的 CPU 总核数
#BSUB -m b07u15a

hostfile=`echo $LSB_DJOB_HOSTFILE`
NP=`cat $hostfile | wc -l`

free | awk 'NR==2 {print $4}' > memory_size.txt
"""


def memory_size(node_name):
    print("Getting memory in node " + node_name)
    # 指定文件名
    file_name = 'memory.lsf'

    # 打开文件并写入内容
    with open(file_name, 'w') as f:
        f.write(memory_size_content)

    # 读取文件内容
    with open(file_name, 'r+') as f:
        file_contents = f.read()

    # 定位需要修改的行
    lines = file_contents.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('#BSUB -m'):
            lines[i] = f"#BSUB -m {node_name}"
            break  # 找到并修改后退出循环

    # 将修改后的内容写回文件
    updated_content = '\n'.join(lines)
    with open(file_name, 'w') as f:
        f.write(updated_content)

    print(f"find memory size on node '{node_name}' with file '{file_name}'")

    os.popen(f"bsub < '{file_name}'")


def read_memory_size():
    file_name = 'memory_size.txt'
    try:
        # 打开文件并读取内容
        with open(file_name, 'r') as f:
            lines = f.readlines()

        # 查找包含 CPU(s) 的行并解析核心数
        for line in lines:
            free_memory_size = int(line)
            print("free_memory_size", free_memory_size)
            return free_memory_size

        # 如果没有找到 CPU(s) 行，默认返回 None 或者适合的错误处理
        return None

    except Exception as e:
        print(f"Error occurred while reading {file_name}: {str(e)}")
        return None
