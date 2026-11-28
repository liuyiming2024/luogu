# P1042 朴素（Python 递归「切出最早完局」，非增量状态机）：
# 每次从头累计找到第一个达标的局，切掉该前缀再递归，最后补当前局。
import sys

def split_one(seq, mode):
    a = b = 0
    for i, ch in enumerate(seq):
        if ch == 'W': a += 1
        else: b += 1
        if max(a, b) >= mode and abs(a-b) >= 2:
            return (a, b), seq[i+1:]
    return None, seq

def games(seq, mode):
    out = []
    while True:
        g, rest = split_one(seq, mode)
        if g is None: break
        out.append("%d:%d" % g)
        seq = rest
    a = seq.count('W'); b = seq.count('L')
    out.append("%d:%d" % (a, b))
    return out

def main():
    raw = sys.stdin.read()
    s = ""
    for ch in raw:
        if ch == 'E': break
        if ch in "WL": s += ch
    print("\n".join(games(s, 11)))
    print()
    print("\n".join(games(s, 21)))

if __name__ == "__main__": main()
