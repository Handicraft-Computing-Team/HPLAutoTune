import asyncio
import threading
import time

# import opentuner
import re
from bayes_opt import BayesianOptimization
from bayes_opt.util import UtilityFunction
from colorama import Fore

import RunHPL

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
file_path = '/testing'
WAITING_TIME = 0.2
COMPILE_TIME = 60

# for bayesian
Kappa = 3
Xi = 1


def black_box_function(N_rate, NBs_rate, NBMIN, BCAST):
    """Function with unknown internals we wish to maximize.

    This is just serving as an example, however, for all intents and
    purposes think of the internals of this function, i.e.: the process
    which generates its outputs values, as unknown.
    """

    HPL_value = 20

    # read HPL's max mem --------------------------------
    N_max = 130000
    N_min = 20000

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
                    N_max = param_value

                if param_name == 'N_min':
                    N_min = param_value

                if param_name == 'NBs_min':
                    NBs_min = param_value

                if param_name == 'NBs_max':
                    NBs_max = param_value

                print(f"Parameter {param_name}: {param_value}")
                parameters[param_name] = param_value

    # calculate HPL's para -----------------------------
    next_N = N_min + (N_max - N_min) * N_rate
    next_NBs = NBs_min + (NBs_max - NBs_min) * NBs_rate
    next_NBmin = round(NBMIN)
    next_BCAST = round(BCAST)

    # write HPL.dat ------------------------------------
    # 将修改后的参数写回文件
    with open(file_path+'/HPL.dat', 'r+') as file:
        lines = file.readlines()
        lines[5] = next_N
        lines[7] = next_NBs
        lines[16] = next_NBmin
        lines[22] = next_BCAST

    # run ----------------------------------------------
    RunHPL.hpl()

    # wait for complete
    time.sleep(WAITING_TIME)

    # read and return result  ---------------------------
    isPassed = False

    # 打开文件并查找包含 "PASSED" 的行
    with open(file_path+'/bayes.txt') as file2:
        for line in file:
            if 'PASSED' in line:
                isPassed = True
                print(line.strip())  # 输出包含 "PASSED" 的行，并去除首尾空白字符

            # 使用正则表达式查找浮点数
            float_pattern = r"[-+]?\d*\.\d+([eE][-+]?\d+)?"
            matches = re.findall(float_pattern, line)

            # 取得匹配到的第一个浮点数并转换为 float
            if matches:
                float_value = float(matches[0])
                if HPL_value < float_value:
                    HPL_value = float_value
                    print(HPL_value)  # 输出转换后的浮点数

    # Result -----------------------------------------------
    # return N_rate**2+N_rate*NBs_rate-NBMIN**2+BCAST**2
    if isPassed:
        return HPL_value
    else:
        return 0


class BayesianOptimizationHandler(RequestHandler):
    """Basic functionality for NLP handlers."""
    HPL_para = {"N_rate": (0, 100), "NBs_rate": (0, 100), "NBMIN": (2, 15), "BCAST": (0, 5)}
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
    global optimizers_config
    config = optimizers_config.pop()
    name = config["name"]
    colour = config["colour"]

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
        print(colour + status, end="\n")

    global results
    results.append((name, max_target))
    print(colour + name + " is done!", end="\n\n")


if __name__ == "__main__":

    RunHPL.compile_hpl()
    time.sleep(COMPILE_TIME)

    ioloop = tornado.ioloop.IOLoop.instance()
    optimizers_config = [
        {"name": "HPL Optimizer", "colour": Fore.GREEN},
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
