# P1061 朴素（**枚举范围内全部 w 元严格递增组合并排序**，定位当前串后取其后 5 个）：
# 不做逐位进位推导；组合数 C(t-s+1,w)，对拍限 w≤6、t-s≤9（如实标注）。
import sys, itertools
def main():
    lines = sys.stdin.read().split("\n")
    s, t, w = map(int, lines[0].split())
    cur = lines[1].strip()
    vals = [ord(c)-ord('a')+1 for c in cur]
    universe = list(range(s, t+1))
    allc = ["".join(chr(ord('a')+x-1) for x in c)
            for c in itertools.combinations(universe, w)]
    key = "".join(chr(ord('a')+x-1) for x in vals)
    i = allc.index(key)
    for x in allc[i+1:i+6]: print(x)
if __name__ == "__main__": main()
