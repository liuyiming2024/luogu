# P1049 朴素（集合 BFS 逐项扩展可达体积，非 DP 数组）：
# reach 为 Python set，每加入一件物品扩展 new = {x+w | x∈reach, x+w≤V}。
import sys
def main():
    d = list(map(int, sys.stdin.read().split()))
    V, n = d[0], d[1]
    ws = d[2:2+n]
    reach = {0}
    for w in ws:
        reach |= {x+w for x in reach if x+w <= V}
    print(V - max(reach))
if __name__ == "__main__": main()
