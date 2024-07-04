import asyncio
import math
# import opentuner
import re
import threading
import time

from bayes_opt import BayesianOptimization
from bayes_opt.util import UtilityFunction

import ClusterInfo
import RunHPL

# from colorama import Fore

try:
    import json
    import tornado.ioloop
    import tornado.httpserver
    from tornado.web import RequestHandler
    import requests
except ImportError:
    raise ImportError(
        "In order to run this example you must have the libraries: " +
        "`tornado` and `requests` installed."
    )

# hyper parameter
Number_of_iter = 30
file_path = '/work/ssc-laihb/haibin/hpl-2.3/testing'
WAITING_TIME = 320
COMPILE_TIME = 60
LSF_TIME = 10

# for bayesian
Kappa = 3
Xi = 1


def black_box_function(N_rate, NBs_rate, NBMIN, BCAST):
    """Function with unknown internals we wish to maximize.

    This is just serving as an example, however, for all intents and
    purposes think of the internals of this function, i.e.: the process
    which generates its outputs values, as unknown.
    """

    alpha_rate = N_rate
    HPL_value = 20

    # read HPL's max mem --------------------------------
    free_memory = 180000

    NBs_max = 512
    NBs_min = 10

    # 读取文件内容并解析参数
    parameters = {}

    # 打开文件
    with open('HPL_Parameter.txt', 'r') as file:
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
                    free_memory = param_value

                if param_name == 'N_min':
                    N_min = param_value

                if param_name == 'NBs_min':
                    NBs_min = param_value

                if param_name == 'NBs_max':
                    NBs_max = param_value

                # print(f"Parameter {param_name}: {param_value}")
                parameters[param_name] = param_value

    # calculate HPL's para -----------------------------

    if 100 - alpha_rate < 2:
        print("May need bigger max_N!")
        # alpha_rate += 2

    next_N = round(math.sqrt((free_memory * 1024 * alpha_rate / 8)) / 10)
    next_NBs = round(NBs_min + ((NBs_max - NBs_min) * NBs_rate) / 100)
    next_NBmin = round(NBMIN)
    next_BCAST = round(BCAST)

    print("next_N:", next_N)
    print("next_NBs:", next_NBs)
    print("next_NBmin:", next_NBmin)
    print("next_BCAST:", next_BCAST)

    # write HPL.dat ------------------------------------
    # 将修改后的参数写回文件
    with open(file_path + '/HPL.dat', 'r+') as file:
        lines = file.readlines()
        lines[5] = str(next_N) + "         Ns\n"
        lines[7] = str(next_NBs) + "          NBs\n"
        lines[16] = str(next_NBmin) + "          NBMINs (>= 1)\n"
        lines[22] = str(next_BCAST) + "            BCASTs (0=1rg,1=1rM,2=2rg,3=2rM,4=Lng,5=LnM)" + "\n"
        # 将更新后的内容写回文件
        file.seek(0)  # 将文件指针移到文件开头
        file.writelines(lines)  # 将修改后的内容写回文件
        file.truncate()  # 截断文件，删除原有内容之后的部分（如果有）

    # 关闭文件
    file.close()

    # run ----------------------------------------------
    RunHPL.hpl()

    # wait for complete
    time.sleep(WAITING_TIME)

    # -- For multi process, this is not good since bjobs may find other thread's process --#
    # count = 0
    # for i in range(30):
    #     res = os.popen(f"bjobs").readlines()
    #     if len(res) >= 1:
    #         time.sleep(10)
    #     else:
    #         time.sleep(4)
    #         count += 1
    #     if count == 5:
    #         break

    # read and return result  ---------------------------
    isPassed = False
    results = []
    # 使用正则表达式查找浮点数
    float_pattern = r"\d+\.\d+e[+-]\d+"

    # 打开文件并查找包含 "PASSED" 的行
    with open(file_path + '/bayes.txt', 'r') as file2:
        for line in file2:
            if 'PASSED' in line:
                isPassed = True
                print(line.strip())  # 输出包含 "PASSED" 的行，并去除首尾空白字符

            matches = re.findall(float_pattern, line)

            # 取得匹配到的第一个浮点数并转换为 float
            if matches:
                float_value = float(matches[0])

                if HPL_value < float_value:
                    # 将所有匹配项添加到结果列表中
                    results.append(float_value)


    # Result -----------------------------------------------
    # return N_rate**2+N_rate*NBs_rate-NBMIN**2+BCAST**2
    if isPassed:
        HPL_value = (results[-1])
        print("last HPL value:", HPL_value)  # 输出转换后的浮点数
        return HPL_value
    else:
        print("HPL DID NOT PASSED")
        return 0


class BayesianOptimizationHandler(RequestHandler):
    """Basic functionality for NLP handlers."""
    HPL_para = {"N_rate": (80, 100), "NBs_rate": (0, 100), "NBMIN": (2, 15), "BCAST": (0, 5)}
    _bo = BayesianOptimization(
        f=black_box_function,
        pbounds=HPL_para
    )
    _uf = UtilityFunction(kind="ucb", kappa=Kappa, xi=Xi)

    def post(self):
        """Deal with incoming requests."""
        body = tornado.escape.json_decode(self.request.body)

        try:
            self._bo.register(
                params=body["params"],
                target=body["target"],
            )
            print("BO has registered: {} points.".format(len(self._bo.space)), end="\n\n")
        except KeyError:
            pass
        finally:
            suggested_params = self._bo.suggest(self._uf)

        self.write(json.dumps(suggested_params))


def run_optimization_app():
    asyncio.set_event_loop(asyncio.new_event_loop())
    handlers = [
        (r"/bayesian_optimization", BayesianOptimizationHandler),
    ]
    server = tornado.httpserver.HTTPServer(
        tornado.web.Application(handlers)
    )
    server.listen(9009)
    tornado.ioloop.IOLoop.instance().start()


def run_optimizer():
    name = "HPL Optimizer"
    # colour = Fore.GREEN

    register_data = {}
    max_target = None
    for _ in range(Number_of_iter):
        status = name + " wants to register: {}.\n".format(register_data)

        resp = requests.post(
            url="http://localhost:9009/bayesian_optimization",
            json=register_data,
        ).json()
        target = black_box_function(**resp)

        register_data = {
            "params": resp,
            "target": target,
        }

        if max_target is None or target > max_target:
            max_target = target

        status += name + " got {} as target.\n".format(target)
        status += name + " will to register next: {}.\n".format(register_data)
        print(status, end="\n")

    global results
    results.append((name, max_target))
    print(name + " is done!", end="\n\n")


def run_on_single_node(node_name):
    print("Try to run bayesian optimization on HPL at node {}\n".format(node_name))

    ClusterInfo.clean_output()

    # Find cpu info
    ClusterInfo.cpu_info(node_name)
    time.sleep(LSF_TIME)
    cpu_cores = ClusterInfo.read_cpu_info()

    # Compile
    RunHPL.compile_hpl_node(node_name, cpu_cores)
    time.sleep(COMPILE_TIME)

    # Change node
    RunHPL.change_hpl_node(node_name, cpu_cores)

    ClusterInfo.memory_size(node_name)
    free_mem = ClusterInfo.read_memory_size()

    # 输出参数到另一个文件
    output_filename = 'HPL_Parameter.txt'
    with open(output_filename, 'w') as output_file:
        output_file.write(f"N_max {free_mem}\n")
        output_file.write(f"N_min 20000\n")
        output_file.write(f"NBs_min 128\n")
        output_file.write(f"NBs_max 512\n")

    P, Q = RunHPL.find_closest_factors(cpu_cores)
    # write HPL.dat ------------------------------------
    # 将修改后的参数写回文件
    with open(file_path + '/HPL.dat', 'r+') as file:
        lines = file.readlines()
        lines[10] = str(P) + "            Ps\n"
        lines[11] = str(Q) + "            Qs\n"

        # 将更新后的内容写回文件
        file.seek(0)  # 将文件指针移到文件开头
        file.writelines(lines)  # 将修改后的内容写回文件
        file.truncate()  # 截断文件，删除原有内容之后的部分（如果有）

    # Run bayesian
    ioloop = tornado.ioloop.IOLoop.instance()

    app_thread = threading.Thread(target=run_optimization_app)
    app_thread.daemon = True
    app_thread.start()

    targets = (
        run_optimizer,
    )
    optimizer_threads = []
    for target in targets:
        optimizer_threads.append(threading.Thread(target=target))
        optimizer_threads[-1].daemon = True
        optimizer_threads[-1].start()

    results = []
    for optimizer_thread in optimizer_threads:
        optimizer_thread.join()

    for result in results:
        print(result[0], "found a maximum value of: {}".format(result[1]))

    ioloop.stop()


if __name__ == "__main__":

    print("welcome to bayesian_optimization on HPL")

    RunHPL.compile_hpl()
    time.sleep(COMPILE_TIME)

    ioloop = tornado.ioloop.IOLoop.instance()
    optimizers_config = [
        {"name": "HPL Optimizer"},
    ]

    app_thread = threading.Thread(target=run_optimization_app)
    app_thread.daemon = True
    app_thread.start()

    targets = (
        run_optimizer,
    )
    optimizer_threads = []
    for target in targets:
        optimizer_threads.append(threading.Thread(target=target))
        optimizer_threads[-1].daemon = True
        optimizer_threads[-1].start()

    results = []
    for optimizer_thread in optimizer_threads:
        optimizer_thread.join()

    for result in results:
        print(result[0], "found a maximum value of: {}".format(result[1]))

    ioloop.stop()
