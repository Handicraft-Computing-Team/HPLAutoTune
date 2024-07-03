import os


def hpl():
    # the file that submit the hpl program
    file_name = 'hpl.lsf'

    print("Running HPL with " + file_name)
    os.popen('bsub < ' + file_name)


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
    file_name = 'hpl.lsf'
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


def get_cpu_info(node_name):
    # 使用正则表达式写入节点名字
    command = 'bhost hg_' + node_name
    command += '>> ' + node_name + '.txt'
    os.system(command)
    print("Running CPU info...")


def compile_hpl():
    print("compiling HPL...")
    os.popen('bsub < compile.lsf')


# 定义要写入文件的内容
compile_content = """
#!/bin/bash
#BSUB -q ssc-cpu ##队列名
#BSUB -J HPL-Test
#BSUB -n 40                   ##申请的 CPU 总核数
#BSUB -m b07u15a

hostfile=`echo $LSB_DJOB_HOSTFILE`
NP=`cat $hostfile | wc -l`


cd /work/ssc-laihb/haibin/hpl-2.3

source /share/intel/oneapi-2023.1/setvars.sh

make arch=Linux_Intel64 clean

./configure

make arch=Linux_Intel64

"""


def compile_hpl_node(node_name, cpu_cores):
    print("compiling HPL on node " + node_name)

    # the file that compile hpl on the target machine
    compile_file = 'compile.lsf'

    # 打开文件并写入内容
    with open(compile_file, 'w') as f:
        f.write(compile_content)

    # 读取文件内容
    with open(compile_file, 'r+') as f:
        compile_1_content = f.read()

    # 定位需要修改的行
    lines = compile_1_content.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('#BSUB -m'):
            lines[i] = f"#BSUB -m {node_name}"
            # break  # 找到并修改后退出循环

        if line.startswith('#BSUB -n'):
            lines[i] = f"#BSUB -n {cpu_cores}"

    # write back the content into file
    updated_content = '\n'.join(lines)
    with open(compile_file, 'w') as f:
        f.write(updated_content)

    print(f"Compiling node '{node_name} with {cpu_cores} cores with file '{compile_file}'")

    os.popen('bsub < ' + compile_file)


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
