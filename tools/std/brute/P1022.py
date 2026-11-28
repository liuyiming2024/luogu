# P1022 朴素：改写成可求值表达式 + 数值二分求根（不同实现路径）。
import sys
def conv(seg):
    out=""
    for ch in seg:
        if ch.isalpha():
            if out and (out[-1].isdigit() or out[-1]=="X"): out+="*"
            out+="X"
        else: out+=ch
    return out
def main():
    s=sys.stdin.read().strip().splitlines()[0]
    L,R=s.split("=")
    expr="("+conv(L)+")-("+conv(R)+")"
    def f(X): return eval(expr,{"__builtins__":{}},{"X":X})
    lo,hi=-1e7,1e7;flo=f(lo)
    if flo*f(hi)>0: lo,hi=-1e9,1e9;flo=f(lo)
    for _ in range(200):
        mid=(lo+hi)/2
        if flo*f(mid)<=0: hi=mid
        else: lo,flo=mid,f(mid)
    x=(lo+hi)/2
    if abs(x)<0.0005: x=0.0
    var=next(ch for ch in s if ch.isalpha())
    ans=x
    print("%s=%.3f"%(var,ans))
if __name__=="__main__": main()
