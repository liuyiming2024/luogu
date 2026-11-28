# P1045 朴素（Python 内置大整数全量展开 2^P-1，完全不同实现路径）：
# 位数用 len(str(实际整数))，不用对数公式；最后 500 位用 % 10**500 后 zfill 分行。
# 全量展开随 P 增长，对拍限 P≤20000（如实标注，不假装覆盖 P<3100000）。
import sys
sys.set_int_max_str_digits(0)

def main():
    P = int(sys.stdin.read().split()[0])
    v = (1 << P) - 1
    print(len(str(v)))
    s = str(v % (10**500)).zfill(500)
    for i in range(0, 500, 50):
        print(s[i:i+50])

if __name__ == "__main__": main()
