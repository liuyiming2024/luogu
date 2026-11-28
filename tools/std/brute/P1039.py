# P1039 朴素（显式枚举「谁说谎」的 2^M 标签组合，从说谎者侧出发，
# 与 std 的「罪犯×星期 → 区间统计」完全不同）：
# 检查每条可识别证词的真值必须与该人标签一致，且说谎人数恰好 N；
# 可行的罪犯集合决定输出。
import sys, itertools

WEEK = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

def parse(names, speaker, content, culprit, day):
    if content == "I am guilty.": return speaker == culprit
    if content == "I am not guilty.": return speaker != culprit
    if content.startswith("Today is ") and content.endswith("."):
        d = content[9:-1]
        if d in WEEK: return d == day
        return None
    for suf, neg in ((" is not guilty.", True), (" is guilty.", False)):
        if content.endswith(suf):
            who = content[:-len(suf)]
            if who in names: return (who != culprit) if neg else (who == culprit)
            return None
    return None

def main():
    lines = sys.stdin.read().split("\n")
    M, N, P = map(int, lines[0].split())
    names = [lines[1+i].strip() for i in range(M)]
    stmts = []
    for i in range(P):
        row = lines[1+M+i]
        if ": " in row:
            a, b = row.split(": ", 1); stmts.append((a.strip(), b.strip()))
        else: stmts.append((row.strip(), ""))
    feasible = set()
    for culprit in names:
        for day in WEEK:
            vals = [parse(names, s, c, culprit, day) for s, c in stmts]
            for mask in range(1 << M):
                if bin(mask).count("1") != N: continue
                ok = True
                for (s, c), t in zip(stmts, vals):
                    if t is None: continue
                    if s not in names: continue
                    sid = names.index(s)
                    liar = bool(mask >> sid & 1)
                    if liar == t: ok = False; break   # 说谎者说真话 / 诚实者说假话
                if ok: feasible.add(culprit); break
    if not feasible: print("Impossible")
    elif len(feasible) > 1: print("Cannot Determine")
    else: print(sorted(feasible)[0])

if __name__ == "__main__": main()
