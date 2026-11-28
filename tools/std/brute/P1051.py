# P1051 朴素（规则表 + reduce/生成器求和，非逐条 if 累加）：
# 把五种奖学金定义成 (谓词, 金额) 列表，对每个学生用 sum() over 规则表计算。
import sys

RULES = [
    (lambda r: r["avg"] > 80 and r["papers"] >= 1, 8000),
    (lambda r: r["avg"] > 85 and r["cls"] > 80, 4000),
    (lambda r: r["avg"] > 90, 2000),
    (lambda r: r["avg"] > 85 and r["west"] == "Y", 1000),
    (lambda r: r["cls"] > 80 and r["leader"] == "Y", 850),
]

def main():
    lines = sys.stdin.read().split("\n")
    N = int(lines[0].split()[0])
    rows = []
    for i in range(N):
        f = lines[1+i].split()
        rows.append({"name": f[0], "avg": int(f[1]), "cls": int(f[2]),
                     "leader": f[3], "west": f[4], "papers": int(f[5])})
    def bonus(r):
        return sum(amount for pred, amount in RULES if pred(r))
    vals = [(r["name"], bonus(r)) for r in rows]
    mx = max(v for _, v in vals)
    winner = next(name for name, v in vals if v == mx)   # 输入顺序最早
    print(winner); print(mx); print(sum(v for _, v in vals))

if __name__ == "__main__": main()
