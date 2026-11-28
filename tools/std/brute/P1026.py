# P1026 朴素：枚举全部 k-1 个切点组合逐段计数（k≤3，如实标注）。
import sys, itertools
def main():
    data=sys.stdin.read().splitlines()
    p,k=map(int,data[0].split())
    s="".join(data[1:1+p]);sd=int(data[1+p]);words=data[2+p:2+p+sd];n=len(s)
    def seg(l,r):
        cnt=0
        for i in range(r,l-1,-1):
            for w in words:
                if i+len(w)<=r+1 and s.startswith(w,i): cnt+=1;break
        return cnt
    best=0
    for cuts in itertools.combinations(range(1,n),k-1):
        b=(0,)+cuts+(n,)
        total=sum(seg(b[i],b[i+1]-1) for i in range(k))
        if total>best: best=total
    ans=best
    print(ans)
if __name__=="__main__": main()
