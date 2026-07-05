import numpy as np
from scipy.special import kv
params = {'Q': 400, 'T': 10, 'S': 0.0001, 'K_prime': 0.0001, 'B_prime': 50, 'rw': 0.2, 'rc': 0.2, 'tau_q': 0.2, 'tau_s': 2, 'Sk': 0, 'r': 10}
Q, T, S, K_prime, B_prime, rw, rc, tq, ts, Sk = 400, 10, 0.0001, 0.0001, 50, 0.2, 0.2, 0.2, 2, 0
r = 10
def laplace_domain_solution(p, params):
    # 1. 計算中間參數 (這些是您公式中的 lambda 與其他係數)
    kappa = params['K_prime'] / (params['B_prime'] * params['T'])
    tau_qD = (params['T'] * params['tau_q']) / (params['S'] * params['rw']**2)
    tau_sD = (params['T'] * params['tau_s']) / (params['S'] * params['rw']**2)
    
    # 計算 Lambda (您代碼中的 k)
    lambda_val = np.sqrt((p + kappa) * (1 + p * tau_qD) / (1 + p * tau_sD))
    
    # 2. 計算貝索函數
    K0 = kv(0, lambda_val)
    K1 = kv(1, lambda_val)
    
    # 3. 定義 CD 和 rD
    CD = params['rc']**2 / (2 * params['S'] * (params['rw']**2))
    rD = params['r'] / params['rw']
    
    # 4. 計算 SD (修正您的公式)
    # 注意：這裡使用 kv(0, lambda_val * rD) 來正確計算 K0(lambda * rD)
    num = 2 * kv(0, lambda_val * rD)
    den = (CD * (p**2) * K0) + (p * (1 + CD * p * params['Sk']) * lambda_val * K1)
    
    return num / den
# def laplace_domain_solution(p):
#     rD = r / rw
#     k = K_prime / (B_prime * T)
#     CD = rc ** 2 / (2 * S * rw * rw)
#     SD=(2.0*(k0(k))*(k*rD))/((CD*(p**2)*(k0(k))*k)+k*p*(1.0+CD*p*Sk)*(k1(k))*k)
#     return SD
import numpy as np
from scipy.special import factorial

def get_stehfest_v(i, N):
    """計算 Stehfest 權重係數 Vi"""
    n2 = N // 2
    v = 0
    # 這是 Stehfest 的標準加權公式
    for k in range((i + 1) // 2, min(i, n2) + 1):
        num = (k**n2) * factorial(2 * k)
        den = factorial(n2 - k) * factorial(k) * factorial(k - 1) * \
              factorial(i - k) * factorial(2 * k - i)
        v += num / den
    
    # 加上正負號項 (-1)^(N/2 + i)
    return ((-1)**(n2 + i)) * v

def stehfest_inversion(func, t, params, N=12):
    ln2 = np.log(2.0)
    s = 0.0
    for i in range(1, N + 1):
        # --- 修正處：呼叫我們剛剛定義好的權重計算 ---
        v = get_stehfest_v(i, N) 
        # ----------------------------------------
        p = i * ln2 / t
        s += v * func(p, params)
    return (ln2 / t) * s

# 設定一系列的時間點 (從 0.1 到 100000000 小時，取 50 個點)
times = np.logspace(-1, 8, 50)
drawdowns = [] # 準備一個空籃子裝水位數據

for t in times:
    sD = stehfest_inversion(laplace_domain_solution, t, params)
    s = sD * (params['Q'] / (4 * np.pi * params['T']))
    
    # 偵錯機制
    if np.isnan(s) or np.isinf(s):
        print(f"在時間 {t} 發生計算錯誤，請檢查公式")
    elif s == 0:
        print(f"在時間 {t} 算出為 0，可能是參數過小或公式除法有誤")
    
    drawdowns.append(s)
import matplotlib.pyplot as plt

# 圖 1: 水位洩降 vs 時間
plt.figure()
plt.plot(times, drawdowns)
plt.title("Drawdown vs Time")
plt.xlabel("Time (h)")
plt.ylabel("Drawdown (m)")

# 圖 2: 水位洩降 vs log 時間
plt.figure()
plt.semilogx(times, drawdowns)
plt.title("Drawdown vs log Time")
plt.xlabel("log(Time) (h)")
plt.ylabel("Drawdown (m)")

plt.show()