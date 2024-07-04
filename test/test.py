import re

import bayes_optM


def ma():
    HPL_value = 20
    # 打开文件并查找包含 "PASSED" 的行
    with open('../bayes.txt', 'r') as file2:
        for line in file2:
            if 'PASSED' in line:
                isPassed = True
                print(line.strip())  # 输出包含 "PASSED" 的行，并去除首尾空白字符

            # 使用正则表达式查找浮点数
            float_pattern = r"\d+\.\d+e[+-]\d+"
            matches = re.findall(float_pattern, line)

            # 取得匹配到的第一个浮点数并转换为 float
            if matches:
                float_value = float(matches[0])
                if HPL_value < float_value:
                    HPL_value = float_value
                    print(HPL_value)  # 输出转换后的浮点数


# ma()


import threading

import concurrent.futures

# 要处理的任务列表
node_list = ['Task1', 'Task2', 'Task3', 'Task4', 'Task5', 'Task6', 'Task7', 'Task8']


# 定义一个任务函数，接受一个参数作为任务
def process_node(node):
    print(f"Thread {threading.current_thread().name} is processing task: {node}")
    # bayes_optM.run_on_single_node(node)


# 创建一个线程池，指定最大线程数为4
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    # 提交每个任务给线程池执行
    futures = {executor.submit(process_node, node): node for node in node_list}

    # 等待所有任务完成
    for future in concurrent.futures.as_completed(futures):
        node = futures[future]
        try:
            result = future.result()
        except Exception as exc:
            print(f'node task {node} generated an exception: {exc}')
        else:
            print(f'node {node} completed successfully')

print("All testing tasks completed")

# N_rate, NBs_rate, NBMIN, BCAST
#
# HPL_value = 20
#
# # read HPL's max mem --------------------------------
# N_max = 130000
# N_min = 20000
#
# NBs_max = 512
# NBs_min = 10
#
# NBMIN = 5
# BCAST = 5
#
# # 读取文件内容并解析参数
parameters = {}
#
# # 打开文件
with open('../HPL_Parameter.txt', 'r') as file:
    # 逐行读取文件内容
    for line in file:
        # 去除行末尾的换行符并按空格分割
        parts = line.strip().split()
        # 如果行不为空
        if parts:
            # 第一个部分是参数名称，第二个部分是浮点数值
            param_name = parts[0]
            param_value = float(parts[1])  # 转换为浮点数
            if param_name == 'N_max':
                N_max = param_value

            if param_name == 'N_min':
                N_min = param_value

            if param_name == 'NBs_min':
                NBs_min = param_value

            if param_name == 'NBs_max':
                NBs_max = param_value

            print(f"Parameter {param_name}: {param_value}")
            parameters[param_name] = param_value
#
# # calculate HPL's para -----------------------------
# next_N = round(N_min + (N_max - N_min))
# next_NBs = round(NBs_min + (NBs_max - NBs_min))
# next_NBmin = round(NBMIN)
# next_BCAST = round(BCAST)
#
# # write HPL.dat ------------------------------------
# # 将修改后的参数写回文件
# with open('HPL.dat', 'r+') as file:
#     lines = file.readlines()
#     lines[5] = str(next_N) + "         Ns\n"
#     lines[7] = str(next_NBs) + "          NBs\n"
#     lines[16] = str(next_NBmin) + "          NBMINs (>= 1)\n"
#     lines[22] = str(next_BCAST) + "            BCASTs (0=1rg,1=1rM,2=2rg,3=2rM,4=Lng,5=LnM)" + "\n"
#     # 将更新后的内容写回文件
#     file.seek(0)  # 将文件指针移到文件开头
#     file.writelines(lines)  # 将修改后的内容写回文件
#     file.truncate()  # 截断文件，删除原有内容之后的部分（如果有）
#
# # 关闭文件
# file.close()


def find_closest_factors(N):
    if N <= 0:
        return None

    min_difference = float('inf')
    best_P = None
    best_Q = None

    # 遍历可能的 P 值
    for P in range(1, int(N ** 0.5) + 1):
        if N % P == 0:
            Q = N // P
            difference = abs(P - Q)
            if difference < min_difference:
                min_difference = difference
                best_P = P
                best_Q = Q

    if best_P is not None and best_Q is not None:
        return best_P, best_Q
    else:
        return None


# # 示例用法
# N = 60
# result = find_closest_factors(N)
# if result:
#     P, Q = result
#     print(f"最接近的两个整数数 P, Q 使得 P * Q = {N} 是: P = {P}, Q = {Q}")
# else:
#     print(f"找不到两个整数 P, Q 使得 P * Q = {N}")



hpl_lsf_content = """
#!/bin/bash
#BSUB -q ssc-cpu ##队列名
#BSUB -J HPL-Test
#BSUB -n 40                   ##申请的 CPU 总核数
#BSUB -m b07u15a

hostfile=`echo $LSB_DJOB_HOSTFILE`
NP=`cat $hostfile | wc -l`


#cd /work/ssc-laihb/haibin/hpl-2.3

source /share/intel/oneapi-2023.1/setvars.sh

#make arch=Linux_Intel64 clean

#./configure

#make arch=Linux_Intel64

cd /work/ssc-laihb/haibin/hpl-2.3/testing

mpirun -np $NP ./xhpl >> bayes.txt
"""


def change_hpl_node(node_name, cpu_cores):
    # the file that submit the hpl program
    file_name = '../hpl.lsf'
    # 打开文件并写入内容
    with open(file_name, 'w') as f:
        f.write(hpl_lsf_content)

    try:
        # 读取文件内容
        with open(file_name, 'r') as f:
            lines = f.readlines()

        # 定位需要修改的行
        for i, line in enumerate(lines):
            if line.startswith('#BSUB -m'):
                lines[i] = f"#BSUB -m {node_name}\n"

            if line.startswith('#BSUB -n'):
                lines[i] = f"#BSUB -n {cpu_cores}\n"

        # 将修改后的内容写回文件
        with open(file_name, 'w') as f:
            f.writelines(lines)

        print(f"Successfully changed node to {node_name} and CPU cores to {cpu_cores}")

    except Exception as e:
        print(f"Error modifying file {file_name}: {e}")

# change_hpl_node("sadfasad", cpu_cores=50)

def modify_file(file_name, node_name, cpu_cores):
    try:
        # 读取文件内容
        with open(file_name, 'r') as f:
            lines = f.readlines()

        # 定位需要修改的行
        for i, line in enumerate(lines):
            if line.startswith('#BSUB -m'):
                lines[i] = f"#BSUB -m {node_name}\n"

            if line.startswith('#BSUB -n'):
                lines[i] = f"#BSUB -n {cpu_cores}\n"

        # 将修改后的内容写回文件
        with open(file_name, 'w') as f:
            f.writelines(lines)

        print(f"Successfully changed node to {node_name} and CPU cores to {cpu_cores}")

    except Exception as e:
        print(f"Error modifying file {file_name}: {e}")
#
# # 示例用法
# file_name = 'your_file.txt'  # 替换为你的文件名
# node_name = 'your_node'     # 替换为你的节点名称
# cpu_cores = 8               # 替换为你的CPU核心数
#
# modify_file(file_name, node_name, cpu_cores)

import concurrent.futures
from functools import partial

def process_node(node, colour):
    # 在这里处理节点任务，并使用 colour 参数
    print(f"Processing node {node} with colour {colour}")

# 示例数据
node_list = ['node1', 'node2', 'node3']
colours = ['red', 'blue', 'green']

# 创建一个线程池，指定最大线程数为4
max_worker = 4
with concurrent.futures.ThreadPoolExecutor(max_workers=max_worker) as executor:
    # 提交每个任务给线程池执行
    for node, colour in zip(node_list, colours):
        executor.submit(process_node, node, colour)

    # 等待所有任务完成
    for future in concurrent.futures.as_completed(futures):
        node = futures[future]
        try:
            result = future.result()
        except Exception as exc:
            print(f'node task {node} generated an exception: {exc}')
        else:
            print(f'node {node} completed successfully')

print("All testing HPL tasks completed")

# 输出参数到另一个文件
output_filename = '../HPL_Parameter.txt'
with open(output_filename, 'w') as output_file:
    output_file.write(f"N_max: {1342332}\n")
    output_file.write(f"N_min: 20000\n")
    output_file.write(f"NBs_min: 32\n")
    output_file.write(f"NBs_max: 512\n")





import math

free_memory = 182226588
alpha_rate = 95
a = round(math.sqrt((free_memory * 1024 * alpha_rate / 8)) / 10)
print(a)
