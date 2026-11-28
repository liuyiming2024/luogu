# P1054 朴素（**栈式优先级求值 + 精确大整数**，与 std 的递归下降 + 模素数指纹完全不同）：
# 两个栈按题面优先级归约（括号 > ^ > * > +-，同级左结合），对 a=1..12 用 Python
# 原生大整数逐点求值，不取模、不用快速幂。表达式长度≤50，对拍用例幂链浅，精确值可控。
import sys

def eval_expr(s, a):
    vals, ops = [], []
    prec = {'+':1, '-':1, '*':2, '^':3}
    def apply():
        if len(ops) < 1 or len(vals) < 2: raise ValueError
        op = ops.pop(); r = vals.pop(); l = vals.pop()
        if op == '+': vals.append(l + r)
        elif op == '-': vals.append(l - r)
        elif op == '*': vals.append(l * r)
        else:
            if r < 0 or r > 10**6: raise ValueError
            vals.append(pow(l, r))
    i = 0
    expect_operand = True
    while i < len(s):
        c = s[i]
        if c == ' ': i += 1; continue
        if c.isdigit():
            j = i
            while j < len(s) and s[j].isdigit(): j += 1
            vals.append(int(s[i:j])); i = j; expect_operand = False; continue
        if c == 'a':
            vals.append(a); i += 1; expect_operand = False; continue
        if c == '(':
            ops.append(c); i += 1; expect_operand = True; continue
        if c == ')':
            while ops and ops[-1] != '(': apply()
            if not ops or ops[-1] != '(': raise ValueError
            ops.pop(); i += 1; expect_operand = False; continue
        if c in prec:
            if expect_operand and c == '-':
                # 允许一元负号（题面数字为正整数，谨慎支持）
                vals.append(0); expect_operand = False
            if expect_operand: raise ValueError
            # 同级左结合：先归约栈顶同级或更高优先级（^ 也必须左结合）
            while (ops and ops[-1] != '(' and prec[ops[-1]] >= prec[c]):
                apply()
            ops.append(c); i += 1; expect_operand = True; continue
        raise ValueError
    if expect_operand: raise ValueError
    while ops:
        if ops[-1] == '(': raise ValueError
        apply()
    if len(vals) != 1: raise ValueError
    return vals[0]

def fingerprint(s):
    try:
        return [eval_expr(s, a) for a in range(1, 13)]
    except Exception:
        return None

def main():
    lines = sys.stdin.read().split("\n")
    if not lines: return
    target = fingerprint(lines[0])
    n = int(lines[1].strip())
    ans = []
    for i in range(n):
        f = fingerprint(lines[2+i])
        if f is not None and target is not None and f == target:
            ans.append(chr(ord('A') + i))
    print("".join(ans))

if __name__ == "__main__": main()
