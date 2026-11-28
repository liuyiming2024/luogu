# P1001 朴素算法：不用整数加法，按十进制字符串逐位竖式相加（含异号大减小）。
import sys

def add_abs(a, b):
    i, j, carry, out = len(a)-1, len(b)-1, 0, []
    while i >= 0 or j >= 0 or carry:
        s = carry
        if i >= 0: s += ord(a[i])-48; i -= 1
        if j >= 0: s += ord(b[j])-48; j -= 1
        out.append(chr(48 + s % 10)); carry = s // 10
    return ''.join(reversed(out)).lstrip('0') or '0'

def sub_abs(a, b):                       # a >= b >= 0
    i, j, borrow, out = len(a)-1, len(b)-1, 0, []
    while i >= 0:
        d = ord(a[i])-48 - borrow - (ord(b[j])-48 if j >= 0 else 0)
        if d < 0: d += 10; borrow = 1
        else: borrow = 0
        out.append(chr(48+d)); i -= 1; j -= 1
    return ''.join(reversed(out)).lstrip('0') or '0'

def ge(a, b): return (len(a), a) >= (len(b), b)

def add(x, y):
    sx = '-' if x.startswith('-') else ''
    sy = '-' if y.startswith('-') else ''
    ax, ay = x.lstrip('-') or '0', y.lstrip('-') or '0'
    if sx == sy:
        r = add_abs(ax, ay)
        return ('-' if sx == '-' and r != '0' else '') + r
    if ge(ax, ay): r, s = sub_abs(ax, ay), sx
    else:          r, s = sub_abs(ay, ax), sy
    return ('-' if s == '-' and r != '0' else '') + r

def main():
    t = sys.stdin.read().split()
    if len(t) < 2: return
    print(add(t[0], t[1]))

if __name__ == "__main__": main()
