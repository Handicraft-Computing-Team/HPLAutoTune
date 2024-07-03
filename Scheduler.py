import concurrent.futures

import bayes_optM as Bayesian

node = "b07u25a"

# 要处理的任务列表
node_list = ['Task1', 'Task2', 'Task3', 'Task4', 'Task5', 'Task6', 'Task7', 'Task8']
colours = ['red', 'blue', 'green']

max_worker = 4


def process_node(node):
    # print(f"Thread {threading.current_thread().name} is processing task: {node}")
    Bayesian.run_on_single_node(node)

from functools import partial
def multiTask():
    # 创建一个线程池，指定最大线程数为4
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_worker) as executor:
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

    print("All testing HPL tasks completed")


print("welcome to run bayesian optimization on HPL")
Bayesian.run_on_single_node(node)

if __name__ == "__main__":
    print("welcome to run bayesian optimization on HPL with max_worker =", max_worker)
    multiTask()
