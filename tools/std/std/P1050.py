# P1050 循环 · std（数论：纯循环 ⟺ n·(n^L−1) ≡ 0 mod 10^k）：
# 设 d=gcd(n,10^k)、q=10^k/d；纯循环要求 gcd(n,q)=1（否则输出 −1），
# 此时 L = n 在模 q 下的乘法阶。q=2^a·5^b，λ(q)=lcm(2^(a−2), 4·5^(b−1))，
# 质因子只有 2 和 5，从 λ 起反复试除并用快速模幂校验即可，无需逐次模拟。
# Python 内置大整数直接处理 k≤100 / n<10^100。
import sys, math

def carmichael(q):
    a = b = 0
    while q % 2 == 0: a += 1; q //= 2
    while q % 5 == 0: b += 1; q //= 5
    l2 = 1 if a <= 1 else (2 if a == 2 else 1 << (a-2))
    l5 = 1 if b == 0 else 4 * (5 ** (b-1))
    return math.lcm(l2, l5)

def main():
    data = sys.stdin.read().split()
    n = int(data[0]); k = int(data[1])
    M = 10 ** k
    g = math.gcd(n, M)
    q = M // g
    if math.gcd(n, q) != 1:
        print(-1); return
    if q == 1:
        # n ≡ 0 mod 10^k：所有幂后 k 位恒为 0，按题面定义 L=1（纯循环）
        print(1); return
    L = carmichael(q)
    for p in (2, 5):
        while L % p == 0 and pow(n % q, L//p, q) == 1 % q:
            L //= p
    print(L)

if __name__ == "__main__": main()
