# P1055 朴素（按 '-' 分段 + zip 权重 + 生成器表达式，不用逐字符累加扫描）：
import sys
from functools import reduce

def main():
    s = sys.stdin.read().strip()
    parts = s.split('-')
    digits = "".join(parts[:3])                    # 前 9 位数字
    chk = 10 if parts[3] == 'X' else int(parts[3])
    total = reduce(lambda acc, pair: acc + pair[0]*pair[1],
                   zip((int(ch) for ch in digits), range(1, 10)), 0)
    r = total % 11
    if r == chk:
        print("Right")
    else:
        tail = 'X' if r == 10 else str(r)
        print("-".join(parts[:3]) + "-" + tail)

if __name__ == "__main__": main()
