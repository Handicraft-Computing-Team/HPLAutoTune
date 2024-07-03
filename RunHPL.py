import os

# the file that submit the hpl program
file_name = 'hpl.lsf'

# the file that compile hpl on the target machine
compile_file = 'compile.lsf'

def hpl():
    print("Running HPL with " + file_name)
    os.popen('bsub < ' + file_name)


hpl_lsf_content = """
#!/bin/bash
#BSUB -q ssc-cpu ##队列名
#BSUB -J HPL-Test
#BSUB -n 40                   ##申请的 CPU 总核数
#BSUB -e %J.err
#BSUB -o %J.out
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
    # 打开文件并写入内容
    with open(file_name, 'w') as f:
        f.write(hpl_lsf_content)

    # 读取文件内容
    with open(file_name, 'r') as f:
        file_contents = f.read()
    # 定位需要修改的行
    lines = file_contents.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('#BSUB -m'):
            lines[i] = f"#BSUB -m {node_name}"

        if line.startswith('#BSUB -n'):
            lines[i] = f"#BSUB -n {cpu_cores}"


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
#BSUB -e %J.err
#BSUB -o %J.out
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
    print("compiling HPL on node" + node_name)



    # 打开文件并写入内容
    with open(compile_file, 'w') as f:
        f.write(compile_content)

    # 读取文件内容
    with open(compile_file, 'r') as f:
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
