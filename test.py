import re

def ma():
    HPL_value = 20
    # 打开文件并查找包含 "PASSED" 的行
    with open('bayes.txt', 'r') as file2:
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

ma()