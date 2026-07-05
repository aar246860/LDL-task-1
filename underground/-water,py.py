from scipy.special import k0, k1
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def SD(Q, r, T, S, tau_q, tau_s, rw, rc, K_prime, B_prime, Sk, m) -> list:
    ans = []
    k = K_prime / (B_prime * T)
    rD = r / rw
    cD = rc ** 2 / (2 * s * rw ** 2)
    p = lambda i : i * log(2) / T

    for i in range(1, T+1):
        SD_i = (2 * k0(k * rD)) / (cD * (p(i) ** 2) * k0(k)
                                   + k * p(i) * (1 + cD * p(i) * Sk) * k1(k))
        ans.append(SD_i)

    return ans