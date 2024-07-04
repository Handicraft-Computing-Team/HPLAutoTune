import optuna
import numpy as np


# 定义目标函数
def objective(trial):
    x = trial.suggest_uniform('x', -10, 10)  # x 是均匀分布的例子

    # 定义高斯分布的超参数
    mean = trial.suggest_float('mean', -5, 5)  # 均值
    std = trial.suggest_float('std', 0.1, 1.0)  # 标准差

    # 计算带有高斯分布超参数影响的函数值
    f_x = (x - mean) ** 2 / (2 * std ** 2)

    return f_x


# 创建一个 Optuna 优化器实例
study = optuna.create_study(direction='minimize')  # 最小化

# 运行优化过程，设定试验次数
study.optimize(objective, n_trials=50)

# 打印最优结果
print('Best trial:')
best_trial = study.best_trial
print(f'  x: {best_trial.params["x"]:.4f}')
print(f'  mean: {best_trial.params["mean"]:.4f}')
print(f'  std: {best_trial.params["std"]:.4f}')
print(f'  f(x): {best_trial.value:.4f}')
