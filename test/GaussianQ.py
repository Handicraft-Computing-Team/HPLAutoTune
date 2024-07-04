import numpy as np
from scipy.stats import norm
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel
from tqdm import tqdm


def PI(x, gpr, y_max, kappa):
    """
    Calculates the Probability of Improvement (PI) acquisition function value for Bayesian optimization.

    Parameters:
        x (array-like): The input points at which to evaluate the acquisition function.
        gpr (GaussianProcessRegressor): The Gaussian process regressor model.
        y_max (float): The maximum observed value of the target function.
        kappa (float): The exploration-exploitation trade-off parameter.

    Returns:
        float: The PI acquisition function value.
    """

    mu, sigma = gpr.predict(x, return_std=True)
    Z = (mu - y_max + kappa) / sigma
    PI = norm.cdf(Z)

    return PI


def EI(x, gpr, y_max, kappa):
    """
    Calculates the Expected Improvement (EI) acquisition function value for Bayesian optimization.

    Parameters:
        x (array-like): The input points at which to evaluate the acquisition function.
        f (function): The target function.
        y_max (float): The maximum observed value of the target function.
        kappa (float): The exploration-exploitation trade-off parameter.

    Returns:
        float: The EI acquisition function value.
    """

    mu, sigma = gpr.predict(x, return_std=True)
    Z = (mu - y_max + kappa) / sigma
    EI = (mu - y_max + kappa) * norm.cdf(Z) + sigma * norm.pdf(Z)

    return EI


def acq_max(ac, gpr, y_max, lb, ub, kappa, n=100):
    """
    Find the maximum of the acquisition function using random search.

    Parameters:
    - ac (function): The acquisition function.
    - gpr (object): The Gaussian Process Regression model.
    - y_max (float): The maximum observed value of the target function.
    - lb (array-like): The lower bounds of the search space.
    - ub (array-like): The upper bounds of the search space.
    - kappa (float): The exploration-exploitation trade-off parameter.
    - n (int): The number of random search trials.

    Returns:
    - x_max (array-like): The input that maximizes the acquisition function.
    """

    # Random search for the maximum of the acquisition function
    x_trials = np.random.uniform(lb, ub, (n, lb.shape[0]))
    y_trials = ac(x_trials, gpr, y_max, kappa)

    if np.all(y_trials <= 0):
        return None

    x_max = x_trials[np.argmax(y_trials)]

    return x_max


def bayesian_optimizer(f, lb, ub, ac, n_iter, kappa, n_random_starts):
    """
    Perform Bayesian optimization.

    Parameters:
        f (function): The objective function to be maximized.
        lb (array-like): The lower bounds for the solution variables.
        ub (array-like): The upper bounds for the solution variables.
        ac (function): The acquisition function to be used.
        n_iter (int): The number of iterations.
        kappa (float): The exploration-exploitation trade-off parameter.
        n_random_starts (int): The number of random starting points.

    Returns:
        array-like: The best solution found.
    """

    kernel = ConstantKernel(constant_value=1.0, constant_value_bounds=(1e-3, 1e3)) * \
             RBF(length_scale=0.5, length_scale_bounds=(1e-3, 1e3))

    gpr = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=3)

    X_train = np.random.uniform(lb, ub, (n_random_starts, lb.shape[0]))
    Y_train = np.array([f(x) for x in X_train]).reshape(-1, 1)

    for i in tqdm(range(n_iter)):
        gpr.fit(X_train, Y_train)

        y_max = np.max(Y_train)
        while True:
            x_next = acq_max(ac, gpr, y_max, lb, ub, kappa)
            if x_next is not None:
                break
        y_next = f(x_next)

        X_train = np.vstack((X_train, x_next.reshape(-1, lb.shape[0])))
        Y_train = np.vstack((Y_train, y_next.reshape(-1, 1)))

    return X_train[np.argmax(Y_train)], X_train


if __name__ == "__main__":
    """Test the Bayesian optimization algorithm."""

    # """1 Dimensional Example"""
    # n_iter = 100
    # n_random_starts = 100
    # kappa = 1
    # lb = np.array([-5])
    # ub = np.array([5])
    # f = lambda x: np.sin(x) + np.random.normal(0, 0.1)
    # x_max, x_list = bayesian_optimizer(f, lb, ub, EI, n_iter, kappa, n_random_starts)
    # print("Best x: ", x_max)
    # print("Best y: ", f(x_max))
    # print("Length of x_list: ", len(x_list))

    """2 Dimensional Example"""
    n_iter = 100
    n_random_starts = 100
    kappa = 1
    lb = np.array([-5, -5])
    ub = np.array([5, 5])
    f = lambda x: np.sum(np.sin(x)) + np.random.normal(0, 0.1)
    x_max, x_list = bayesian_optimizer(f, lb, ub, EI, n_iter, kappa, n_random_starts)
    print("Best x: ", x_max)
    print("Best y: ", f(x_max))
