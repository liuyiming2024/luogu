import os,json,random,subprocess
B="/data/workspace/luogu_hack/build/r7"
def cc(name,src):
    p=f"{B}/{name}.cpp";e=f"{B}/{name}"
    open(p,"w",encoding="utf-8").write(src)
    r=subprocess.run(["g++","-std=c++17","-O2","-o",e,p],capture_output=True,text=True)
    return e,(r.stderr[:400] if r.returncode else ""),r.returncode
def run(e,inp,t=30):
    p=subprocess.run([e],input=inp,capture_output=True,text=True,timeout=t)
    return p.stdout.strip(),p.returncode
R={}

# --- P1421 真正拼装版（独立进程复核甲类反例） ---
s1421=r"""
#include <bits/stdc++.h>
using namespace std;
int main(){
 double a,b;
 int sum=0;
 cin>>a>>b;
 b=b/10;
 a=a+b;
 while(a>=1.9){ a=a-1.9; sum++; }
 cout<<sum<<endl;
 return 0;
}
"""
e,err,ce=cc("p1421_real",s1421)
R["P1421_real"]={"compile_error":err}
if not ce:
    R["P1421_real"]["cases"]=[]
    for a,b in [(7,6),(19,0),(10,3),(1,9),(3,8),(0,0)]:
        o,rc=run(e,f"{a} {b}\n")
        R["P1421_real"]["cases"].append({"input":f"{a} {b}","expected":(10*a+b)//19,"actual":o,"hacked":o!=str((10*a+b)//19)})

# --- P1014 v6gwt3bu 二分参考代码 ---
s1014=r"""
#include <bits/stdc++.h>
using namespace std;
int main(){
 long long l=1,r,mid,n,a;
 cin>>n; r=n;
 while(l<r){ mid=(l+r)/2; if(mid*(mid+1)/2<n) l=mid+1; else r=mid; }
 a=n-l*(l-1)/2;
 if(l%2==0) cout<<a<<'/'<<l+1-a; else cout<<l+1-a<<'/'<<a;
 return 0;
}
"""
e,err,ce=cc("p1014_v6gwt3bu",s1014)
R["P1014_v6gwt3bu"]={"compile_error":err}
if not ce:
    def ok(N):
        l,r=1,5000
        while l<r:
            m=(l+r)//2
            if m*(m+1)//2>=N:r=m
            else:l=m+1
        k=l;n=N-(k-1)*k//2
        return f"{n}/{k+1-n}" if k%2==0 else f"{k+1-n}/{n}"
    rnd=random.Random(20261121);bad=[];tested=0
    pts=list(range(1,2000))+[rnd.randint(1,10**7) for _ in range(500)]+[10**7]
    for N in pts:
        exp=ok(N);o,rc=run(e,f"{N}\n")
        tested+=1
        if o!=exp: bad.append({"N":N,"expected":exp,"actual":o})
    R["P1014_v6gwt3bu"].update({"tested":tested,"mismatch":len(bad),"examples":bad[:4]})

# --- P1046 f8ckkhfz ---
s1046=r"""
#include <bits/stdc++.h>
using namespace std;
int a[20];
int main(){ int n,cnt=0;
 for(int i=1;i<=10;i++) cin>>a[i];
 cin>>n;
 for(int i=1;i<=10;i++) if(n+30>=a[i]) cnt++;
 cout<<cnt<<endl;
 return 0; }
"""
e,err,ce=cc("p1046_f8ckkhfz",s1046)
R["P1046_f8ckkhfz"]={"compile_error":err}
if not ce:
    rnd=random.Random(20261121);bad=[];tested=0
    for t in range(300):
        hs=[rnd.randint(50,300) for _ in range(10)];h=rnd.randint(100,120)
        exp=sum(1 for x in hs if h+30>=x)
        inp=" ".join(map(str,hs))+f"\n{h}\n"
        o,rc=run(e,inp);tested+=1
        if o!=str(exp):bad.append({"input":inp.strip().replace("\n"," / "),"expected":exp,"actual":o})
    R["P1046_f8ckkhfz"].update({"tested":tested,"mismatch":len(bad),"examples":bad[:4]})

print(json.dumps(R,ensure_ascii=False,indent=2))
json.dump(R,open(f"{B}/results_extra.json","w",encoding="utf-8"),ensure_ascii=False,indent=2)
