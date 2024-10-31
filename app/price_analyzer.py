import numpy as np
from scipy import stats


def calculate_dependent_movement(independent_values, dependent_values):
    """
    Вычисляет собственное движение зависимой величины на основе линейной регрессии.

    :param independent_values: Массив независимой величины (например, цены BTC).
    :param dependent_values: Массив зависимой величины (например, цены ETH).
    :return: Массив декуплированных значений зависимой величины.
    """
    # Проверка, что массивы имеют одинаковую длину
    if len(independent_values) != len(dependent_values):
        raise ValueError(
            "Длины массивов независимой и зависимой величины должны совпадать."
        )

    # Выполнение линейной регрессии
    slope, intercept, r_value, p_value, std_err = stats.linregress(
        independent_values, dependent_values
    )

    return slope, intercept
