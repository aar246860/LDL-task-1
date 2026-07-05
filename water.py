import numpy as np
from math import factorial

def stehfest_coeff(N=12):

    V = np.zeros(N)

    for i in range(1, N+1):

        summation = 0

        k_min = int((i+1)/2)
        k_max = min(i, N//2)

        for k in range(k_min, k_max+1):

            num = (
                k**(N//2)
                * factorial(2*k)
            )

            den = (
                factorial(N//2-k)
                * factorial(k)
                * factorial(k-1)
                * factorial(i-k)
                * factorial(2*k-i)
            )

            summation += num/den

        V[i-1] = (
            (-1)**(N//2+i)
            * summation
        )

    return V
from scipy.special import k0

def LDL_laplace(p,Q,r,T,S,tau_q,tau_s):

    lam = np.sqrt(
        S*p*(1+tau_q*p)
        /
        (T*(1+tau_s*p))
    )

    return (
        Q/(2*np.pi*T)
        *
        k0(lam*r)
        /
        p
    )
def LDL_stehfest(
    t,Q,r,T,S,tau_q,tau_s,
    N=12
):

    V = stehfest_coeff(N)

    ln2 = np.log(2)

    total = 0

    for i in range(1,N+1):

        p = i*ln2/t

        total += (
            V[i-1]
            *
            LDL_laplace(
                p,Q,r,T,S,
                tau_q,tau_s
            )
        )

    return ln2/t * total
times = np.logspace(
    0,
    5,
    100
)
drawdown = []

for t in times:

    s = LDL_stehfest(
        t,
        Q=0.001,
        r=20,
        T=1e-3,
        S=1e-4,
        tau_q=50,
        tau_s=10
    )

    drawdown.append(s)

# 水位洩降 vs 時間圖
import matplotlib.pyplot as plt

plt.figure()

plt.plot(times,drawdown)

plt.xlabel("Time (s)")
plt.ylabel("Drawdown (m)")
plt.title("LDL Pumping Test")

plt.grid()

plt.show()
# 水位洩降 vs log(Time)
plt.figure()

plt.semilogx(
    times,
    drawdown
)

plt.xlabel("log(Time)")
plt.ylabel("Drawdown (m)")
plt.title("LDL Semi-log")

plt.grid()

plt.show()