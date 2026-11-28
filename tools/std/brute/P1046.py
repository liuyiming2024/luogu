# P1046 朴素（排序 + 二分上界计数，非线性扫描）：
import sys, bisect
def main():
    d = list(map(int, sys.stdin.read().split()))
    hs = sorted(d[:10]); reach = d[10]
    print(bisect.bisect_right(hs, reach+30))
if __name__ == "__main__": main()
