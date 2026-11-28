# P1036 朴素（Python itertools 组合 + 确定性 Miller-Rabin，完全不同实现）：
# std 是 C++ DFS + 试除；这里是标准库组合枚举 + 概率/确定性素性测试。
import sys, itertools

def is_prime(v):
    if v < 2: return False
    for p in (2,3,5,7,11,13,17,19,23,29,31,37):
        if v % p == 0: return v == p
    d = v-1; s = 0
    while d % 2 == 0: d //= 2; s += 1
    for a in (2, 325, 9375, 28178, 450775, 9780504, 1795265022):
        a %= v
        if a == 0: continue
        x = pow(a, d, v)
        if x == 1 or x == v-1: continue
        for _ in range(s-1):
            x = x*x % v
            if x == v-1: break
        else: return False
    return True

def main():
    data = sys.stdin.read().split()
    n, k = int(data[0]), int(data[1])
    x = list(map(int, data[2:2+n]))
    ans = 0
    for c in itertools.combinations(x, k):
        if is_prime(sum(c)): ans += 1
    print(ans)

if __name__ == "__main__": main()
