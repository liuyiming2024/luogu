# P1050 朴素（按题面直译：逐次乘 n 取后 k 位，记录每个状态首次出现位置）：
# 不预先做任何数论推导。发现重复且首次出现位置为 1 ⇒ L=a−1（对任意 a 成立）；
# 首次出现位置 >1 ⇒ 存在预周期，按题面「循环不存在」输出 −1。
# 状态数 10^k，对拍限 k≤3（如实标注，不假装覆盖 k≤100）。
import sys

def main():
    data = sys.stdin.read().split()
    n = int(data[0]); k = int(data[1])
    M = 10 ** k
    r = n % M
    seen = {}
    a = 1
    while True:
        if r in seen:
            p = seen[r]
            print(a - p if p == 1 else -1)
            return
        seen[r] = a
        r = (r * n) % M
        a += 1
        if a > 200000:      # 安全上限，对拍范围内不会触发
            print(-1); return

if __name__ == "__main__": main()
