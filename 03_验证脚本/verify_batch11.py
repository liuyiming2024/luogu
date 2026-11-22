#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第 11 批验证（三类口径）
补最小外壳后只验核心逻辑；搜索摘要 != 正文；片段先回原文逐字复核。
逐字源码（全部 8 位 lid）：
  P1067 hu58r34f   https://www.luogu.com/article/hu58r34f
  P1100 qle49r7h   https://www.luogu.com/article/qle49r7h
  P1308 03xk59dp   https://www.luogu.com/article/03xk59dp
  P1150 aceg4kbr   https://www.luogu.com/article/aceg4kbr  (解法一/解法二 两块)
  P1042 m16r8nbd   https://www.luogu.com/article/m16r8nbd
  P1706 jm3biw0r   https://www.luogu.com/article/jm3biw0r
  P1706 wiofo14v   https://www.luogu.com/article/wiofo14v
  P1739 z3dolqp8   https://www.luogu.com/article/z3dolqp8
  P3397 smtoxvvs   https://www.luogu.com/article/smtoxvvs
  P1116 vt4bqm6v   https://www.luogu.com/article/vt4bqm6v
  P2089 vgwp3k30   https://www.luogu.com/article/vgwp3k30
"""
import os, json, random, subprocess, itertools

BASE = "/data/workspace/luogu_hack/build/r11"
os.makedirs(BASE, exist_ok=True)
R = {}

def cc(name, src):
    p = os.path.join(BASE, name + ".cpp"); e = os.path.join(BASE, name)
    open(p, "w", encoding="utf-8").write(src)
    r = subprocess.run(["g++", "-std=c++17", "-O2", "-o", e, p], capture_output=True, text=True)
    return e, (r.stderr[:700] if r.returncode else ""), r.returncode

def run(exe, inp, t=25):
    try:
        p = subprocess.run([exe], input=inp, capture_output=True, text=True, timeout=t)
        return p.stdout, p.returncode, p.stderr[:300]
    except subprocess.TimeoutExpired:
        return "<TIMEOUT>", -9, ""

# =====================================================================
# 1. P1067 hu58r34f —— 多项式输出（含两个个性化 #define 宏）
# =====================================================================
S1067 = r"""
#include<bits/stdc++.h>
#define unique2648 return
#define code 0
using namespace std;
int main(){
    int n,x;
    cin >> n;
    for (int i = n;i >= 0;i--){
        cin >> x;
        if (x!=0){
            if (x>0&&i!=n){ cout << "+"; }
            if (abs(x)!=1||i==0) cout << x;
            else if(x==-1) cout << "-";
            if (i>=2) cout << "x^" << i;
            else if (i==1) cout << "x";
        }
    }
    unique2648 code;
}
"""
def ok1067(coef):
    # coef: [a_n, ..., a_0]，题面保证 a_n != 0
    n = len(coef)-1
    out = []
    for idx, x in enumerate(coef):
        i = n - idx
        if x == 0: continue
        sign = ""
        if x > 0:
            if idx != 0: sign = "+"
        else:
            sign = "-"
        if abs(x) != 1 or i == 0:
            num = str(abs(x))
        else:
            num = ""
        exp = ("x^"+str(i)) if i>=2 else ("x" if i==1 else "")
        out.append(sign+num+exp)
    return "".join(out) if out else "0"

e,err,ce=cc("s1067",S1067)
R["P1067_hu58r34f"]={"compile_error":err}
if not ce:
    fixed=[([100,-1,1,-3,0,10],"官方样例1"),([-50,0,0,1],"官方样例2"),
           ([1],"n=0 系数1"),([-1],"n=0 系数-1"),([5,1,-1,0,3],"混合"),
           ([1,0,0,0,1],"中间零"),([-2,0,-1],"负首项"),([1,-1,1,-1,1],"全±1")]
    cases=[]
    for coef,label in fixed:
        inp=f"{len(coef)-1}\n"+" ".join(map(str,coef))+"\n"
        exp=ok1067(coef); o,rc,_=run(e,inp)
        cases.append({"label":label,"input":inp.strip().replace("\n"," / "),"expected":exp,"actual":o.strip(),"hacked":o.strip()!=exp})
    R["P1067_hu58r34f"]["cases"]=cases
    # 题面 a_n != 0，但仍跑「首项系数为 0」的越界输入看差异（登记为口径，不判缺陷）
    edge_inp="2\n0 0 5\n"
    o,rc,_=run(e,edge_inp)
    R["P1067_hu58r34f"]["leading_zero_coef"]={"input":"2 / 0 0 5","actual":o.strip(),
        "note":"题面 a_n!=0 保证首项非零，此输入不合规；仅记录行为，不计缺陷"}
    for label,inp2 in [("n=0 且 a0=0","0\n0\n"),("全 0 系数","3\n0 0 0 0\n"),
                       ("hack 数据 n=100 首项 1","100\n"+" ".join(["1"]+["0"]*100)+"\n")]:
        o2,rc2,_=run(e,inp2)
        R["P1067_hu58r34f"].setdefault("out_of_spec_edges",[]).append(
            {"label":label,"input":inp2.strip().replace("\n"," / ")[:120],"actual":repr(o2[:80])})
    rnd=random.Random(20261122);mism=0;tested=0
    for _ in range(300):
        n=rnd.randint(0,20)
        coef=[rnd.randint(-100,100) for _ in range(n+1)]
        if coef[0]==0: coef[0]=rnd.choice([-1,1])*rnd.randint(1,100)
        inp=f"{n}\n"+" ".join(map(str,coef))+"\n"
        exp=ok1067(coef); o,rc,_=run(e,inp); tested+=1
        if o.strip()!=exp: mism+=1
    R["P1067_hu58r34f"].update({"random_tested":tested,"mismatch":mism})

# =====================================================================
# 2. P1100 qle49r7h —— 高低位交换（转二进制字符串模拟）
# =====================================================================
S1100 = r"""
#include<bits/stdc++.h>
using namespace std;
long long n;
string zhuan(long long ans)
{
	string a="";
	while(ans)
	{
		a=char(ans%2+48)+a;
		ans/=2;
	}
	for(int i=1;a.size()<32;i++)
	{
		a='0'+a;
	}
	return a;
}
string huan(string a)
{
	string b="";
	for(int i=16;i<32;i++) b+=a[i];
	for(int i=0;i<16;i++) b+=a[i];
	return b;
}
long long jieguo(string a)
{
	long long k=1,sum=0;
	for(int i=a.size()-1;i>=0;i--)
	{
		sum+=(int(a[i])-48)*k;
		k*=2;
	}
	return sum;
}
int main()
{
	cin>>n;
	cout<<jieguo(huan(zhuan(n)));
	return 0;
}
"""
def ok1100(n): return str(((n & 0xFFFF) << 16) | (n >> 16))
e,err,ce=cc("s1100",S1100)
R["P1100_qle49r7h"]={"compile_error":err}
if not ce:
    fixed=[1314520,0,1,65535,65536,4294967295,2147483648,249036820,0xFFFF0000,0x12345678]
    cases=[]
    for n in fixed:
        o,rc,_=run(e,f"{n}\n"); exp=ok1100(n)
        cases.append({"input":n,"expected":exp,"actual":o.strip(),"hacked":o.strip()!=exp})
    R["P1100_qle49r7h"]["cases"]=cases
    rnd=random.Random(20261122);mism=0;tested=0
    for _ in range(300):
        n=rnd.randint(0,2**32-1)
        o,rc,_=run(e,f"{n}\n"); exp=ok1100(n); tested+=1
        if o.strip()!=exp: mism+=1
    R["P1100_qle49r7h"].update({"random_tested":tested,"mismatch":mism})

# =====================================================================
# 3. P1308 03xk59dp —— 统计单词数
# =====================================================================
S1308 = r"""
#include<bits/stdc++.h>
using namespace std;
string dan,ci,s;
int cur=-1,ans;
int main()
{
    cin>>ci;
    for(int i=0;i<ci.size();++i)ci[i]=tolower(ci[i]);
    getchar();
    getline(cin,s);
    s+=' ';
    for(int i=0;i<s.size();++i)s[i]=tolower(s[i]);
    for(int i=0;i<s.size();++i){
        if(s[i]==' '){
            if(dan==ci){ ans++; if(cur==-1)cur=i-ci.size(); }
            dan="";
        }
        else dan+=s[i];
    }
    if(ans==0)printf("-1");
    else printf("%d %d",ans,cur);
    return 0;
}
"""
def ok1308(word, art):
    w=word.lower(); parts=art.lower().split(' ')
    cnt=0; first=-1; pos=0
    for p in parts:
        if p==w:
            cnt+=1
            if first==-1: first=pos
        pos+=len(p)+1
    return "-1" if cnt==0 else f"{cnt} {first}"
e,err,ce=cc("s1308",S1308)
R["P1308_03xk59dp"]={"compile_error":err}
if not ce:
    fixed=[("To","to be or not to be is a question"),
           ("to","Did the Ottoman Empire lose its power at that time"),
           ("a","a A a"),("abc","abc abcd abc"),("x","x"),
           ("to","  to   to  "),("a","aaa a aA a"),("to","TO to To tO"),
           ("q","to be or not"),("a","a  a   a")]
    cases=[]
    for w,art in fixed:
        inp=f"{w}\n{art}\n"; exp=ok1308(w,art); o,rc,_=run(e,inp)
        cases.append({"input":f"{w} / {art}","expected":exp,"actual":o.strip(),"hacked":o.strip()!=exp})
    R["P1308_03xk59dp"]["cases"]=cases
    rnd=random.Random(20261122);mism=0;tested=0;ex=[]
    words=["a","to","abc","xY","q","test","AbC"]
    for _ in range(300):
        w=rnd.choice(words)
        parts=[]
        for _ in range(rnd.randint(1,12)):
            parts.append(rnd.choice([w,w.upper(),w.lower(),"".join(rnd.choice("abcdefg") for _ in range(rnd.randint(1,6))),""]))
        art=" ".join(parts)
        if rnd.random()<0.3: art=" "+art
        inp=f"{w}\n{art}\n"; exp=ok1308(w,art); o,rc,_=run(e,inp); tested+=1
        if o.strip()!=exp:
            mism+=1
            if len(ex)<4: ex.append({"input":f"{w} / {art}","expected":exp,"actual":o.strip()})
    R["P1308_03xk59dp"].update({"random_tested":tested,"mismatch":mism,"examples":ex})

# =====================================================================
# 4. P1150 aceg4kbr —— Peter 的烟（两块代码都验）
# =====================================================================
S1150_A = r"""
#include <iostream>
using namespace std;
int main(){
    int n, k; scanf("%d %d",&n,&k);
    int count = 0;
    int end = 0;
    do {
        count += n;
        end += n;
        n = end / k;
        end %= k;
    } while (n > 0);
    printf("%d\n",count);
    return 0;
}
"""
S1150_B = r"""
#include <stdio.h>
int main(){ int n,k; scanf("%d%d",&n,&k); printf("%d",n+(n-1)/(k-1)); return 0; }
"""
def ok1150(n,k): return str(n+(n-1)//(k-1))
for tag,src in [("A",S1150_A),("B",S1150_B)]:
    e,err,ce=cc("s1150_"+tag,src)
    R.setdefault("P1150_aceg4kbr",{})[tag]={"compile_error":err}
if all(v.get("compile_error")=="" for v in R["P1150_aceg4kbr"].values()):
    fixed=[(4,3),(10,3),(2,2),(100,2),(100000000,2),(100000000,100000000),(3,3),(7,4),(1,2)]
    cases=[]
    for n,k in fixed:
        inp=f"{n} {k}\n"; exp=ok1150(n,k)
        row={"input":f"{n} {k}","expected":exp}
        for tag in ["A","B"]:
            o,rc,_=run(f"{BASE}/s1150_{tag}",inp)
            row[tag]=o.strip(); row[tag+"_rc"]=rc
        row["hacked"]=row["A"]!=exp or row["B"]!=exp
        cases.append(row)
    R["P1150_aceg4kbr"]["cases"]=cases
    rnd=random.Random(20261122);stats={t:{"tested":0,"mismatch":0} for t in ["A","B"]}
    for _ in range(300):
        n=rnd.randint(2,10**8); k=rnd.randint(2,10**8)
        inp=f"{n} {k}\n"; exp=ok1150(n,k)
        for tag in ["A","B"]:
            o,rc,_=run(f"{BASE}/s1150_{tag}",inp)
            stats[tag]["tested"]+=1
            if o.strip()!=exp or rc!=0: stats[tag]["mismatch"]+=1
    R["P1150_aceg4kbr"]["random"]=stats

# =====================================================================
# 5. P1042 m16r8nbd —— 乒乓球
# =====================================================================
S1042 = r"""
#include<bits/stdc++.h>
using namespace std;
char s[250000];
char S;
int len=0;
int main(){
    int w=0,l=0;
    while(cin>>S){ if(S=='E') break; s[len++]=S; }
    for(int i=0;i<len;i++){
        if(s[i]=='W') w++; else l++;
        if(max(w,l)>=11&&abs(w-l)>=2) cout<<w<<":"<<l<<endl,w=0,l=0;
    }
    cout<<w<<":"<<l<<endl,w=0,l=0;
    puts("");
    for(int i=0;i<len;i++){
        if(s[i]=='W') w++; else l++;
        if(max(w,l)>=21&&abs(w-l)>=2) cout<<w<<":"<<l<<endl,w=0,l=0;
    }
    cout<<w<<":"<<l,w=0,l=0;
    return 0;
}
"""
def ok1042(rec):
    res=[]
    for target in (11,21):
        w=l=0
        for c in rec:
            if c=='W': w+=1
            else: l+=1
            if max(w,l)>=target and abs(w-l)>=2:
                res.append(f"{w}:{l}"); w=l=0
        res.append(f"{w}:{l}")
        if target==11: res.append("")   # 空行
    return "\n".join(res)
e,err,ce=cc("s1042",S1042)
R["P1042_m16r8nbd"]={"compile_error":err}
if not ce:
    fixed=["WWWWWWWWWWWWWWWWWWWWWWLWWWWWWWWWWWWWWWWWWWWWWWLW",
           "E","W"*11+"E","W"*10+"L"*11+"E","WL"*30+"E","W"*25+"L"*3+"E"]
    cases=[]
    for rec in fixed:
        inp="\n".join([rec[i:i+25] for i in range(0,len(rec),25)])+"\n"
        exp=ok1042(rec.replace("E",""))
        o,rc,_=run(e,inp)
        # 代码末尾无换行，正确解末尾也无换行
        cases.append({"label":f"len={len(rec.replace('E',''))}","expected":exp,"actual":o.rstrip("\n"),"hacked":o.rstrip("\n")!=exp})
    R["P1042_m16r8nbd"]["cases"]=cases
    rnd=random.Random(20261122);mism=0;tested=0
    for _ in range(200):
        rec="".join(rnd.choice("WL") for _ in range(rnd.randint(0,300)))
        inp="\n".join([rec[i:i+25] for i in range(0,len(rec),25)])+"\nE\n"
        exp=ok1042(rec); o,rc,_=run(e,inp); tested+=1
        if o.rstrip("\n")!=exp: mism+=1
    R["P1042_m16r8nbd"].update({"random_tested":tested,"mismatch":mism})

# =====================================================================
# 6/7. P1706 两篇全排列
# =====================================================================
S1706_J = r"""
#include<bits/stdc++.h>
using namespace std;
int a[10]={0,1,2,3,4,5,6,7,8,9},n;
int main(){
    scanf("%d",&n);
    while(1){
        for(register int i=1;i<=n;++i) printf("%5d",a[i]);
        putchar('\n');
        if(!next_permutation(a+1,a+n+1)) break;
    }
    return 0;
}
"""
S1706_W = r"""
#include<bits/stdc++.h>
using namespace std;
int arr[15];
int vis[15];
int n;
void dfs(int k){
    if (k>n){
        for (int i=1;i<=n;i++){ cout << setw(5) << arr[i]; }
        puts("");
        return;
    }
    for (int i=1;i<=n;i++){
        if (vis[i]!=1){ arr[k]=i; vis[i]=1; dfs(k+1); vis[i]=0; }
    }
}
int main(){ scanf("%d",&n); dfs(1); return 0; }
"""
def ok1706(n):
    return "".join("".join(f"{x:5d}" for x in p)+"\n" for p in itertools.permutations(range(1,n+1)))
for tag,src in [("jm3biw0r",S1706_J),("wiofo14v",S1706_W)]:
    e,err,ce=cc("s1706_"+tag,src)
    R.setdefault("P1706",{})[tag]={"compile_error":err}
if all(v.get("compile_error")=="" for v in R["P1706"].values()):
    cases=[]
    for n in [1,2,3,4,5,6,9]:
        exp=ok1706(n); row={"n":n}
        for tag in ["jm3biw0r","wiofo14v"]:
            o,rc,_=run(f"{BASE}/s1706_{tag}",f"{n}\n",t=60)
            row[tag]="MATCH" if o==exp else f"DIFF rc={rc}"
        cases.append(row)
    R["P1706"]["cases"]=cases

# =====================================================================
# 8. P1739 z3dolqp8 —— 表达式括号匹配
# =====================================================================
S1739 = r"""
#include<bits/stdc++.h>
using namespace std;
int main(){
    char str[300];
    int count = 0;
    scanf("%s", str);
    for(int i = 0; str[i] != '@'; i++){
        if(str[i] == '(') count++;
        else if(str[i] == ')') count--;
        if(count < 0) break;
    }
    printf(count == 0 ? "YES\n" : "NO\n");
    return 0;
}
"""
def ok1739(s):
    c=0
    for ch in s:
        if ch=='@': break
        if ch=='(': c+=1
        elif ch==')': c-=1
        if c<0: return "NO"
    return "YES" if c==0 else "NO"
e,err,ce=cc("s1739",S1739)
R["P1739_z3dolqp8"]={"compile_error":err}
if not ce:
    fixed=["2*(x+y)/(1-x)@","(25+x)*(a*(a+b+b)@","(())@","()()@","))((@","(()@","@","((a+b)@","a)b(c@"]
    cases=[]
    for s in fixed:
        o,rc,_=run(e,s+"\n"); exp=ok1739(s)
        cases.append({"input":s,"expected":exp,"actual":o.strip(),"hacked":o.strip()!=exp})
    R["P1739_z3dolqp8"]["cases"]=cases
    rnd=random.Random(20261122);mism=0;tested=0
    for _ in range(300):
        s="".join(rnd.choice("()ab+-*/") for _ in range(rnd.randint(0,60)))+"@"
        o,rc,_=run(e,s+"\n"); exp=ok1739(s); tested+=1
        if o.strip()!=exp: mism+=1
    R["P1739_z3dolqp8"].update({"random_tested":tested,"mismatch":mism})

# =====================================================================
# 9. P3397 smtoxvvs —— 地毯（二维差分）
# =====================================================================
S3397 = r"""
#include<bits/stdc++.h>
#define N 1010
int n,m; int map[N][N],d[N][N];
struct node { int x1,y1,x2,y2; };
node a[N];
namespace WalkerV {
    void Read() {
		scanf("%d%d",&n,&m);
		for(int i=1;i<=m;i++) scanf("%d%d%d%d",&a[i].x1,&a[i].y1,&a[i].x2,&a[i].y2);
		return;
    }
    void Solve() {
		for(int i=1;i<=m;i++) {
			d[a[i].x1][a[i].y1]++;
			d[a[i].x2+1][a[i].y1]--;
			d[a[i].x1][a[i].y2+1]--;
			d[a[i].x2+1][a[i].y2+1]++;
		}
		for(int i=1;i<=n;i++)
			for(int j=1;j<=n;j++)
				map[i][j]=map[i][j-1]+map[i-1][j]-map[i-1][j-1]+d[i][j];
		return;
    }
    void Print() {
		for(int i=1;i<=n;i++)
			for(int j=1;j<=n;j++)
				printf("%d%c",map[i][j],j==n?'\n':' ');
		return;
    }
}
int main(){ WalkerV::Read(); WalkerV::Solve(); WalkerV::Print(); return 0; }
"""
def ok3397(n,rects):
    g=[[0]*(n+1) for _ in range(n+1)]
    for x1,y1,x2,y2 in rects:
        for i in range(x1,x2+1):
            for j in range(y1,y2+1): g[i][j]+=1
    return "\n".join(" ".join(str(g[i][j]) for j in range(1,n+1)) for i in range(1,n+1))+"\n"
e,err,ce=cc("s3397",S3397)
R["P3397_smtoxvvs"]={"compile_error":err}
if not ce:
    fixed=[(5,[(2,2,3,3),(3,3,5,5),(1,2,1,4)]),
           (1,[(1,1,1,1)]),(3,[(1,1,3,3)]),(4,[(2,2,2,2),(1,1,4,4)]),
           (2,[])]
    cases=[]
    for n,rects in fixed:
        inp=f"{n} {len(rects)}\n"+"".join(f"{x1} {y1} {x2} {y2}\n" for x1,y1,x2,y2 in rects)
        exp=ok3397(n,rects); o,rc,_=run(e,inp)
        cases.append({"label":f"n={n} m={len(rects)}","expected":exp.strip().replace("\n"," / "),"actual":o.strip().replace("\n"," / "),"hacked":o!=exp})
    R["P3397_smtoxvvs"]["cases"]=cases
    rnd=random.Random(20261122);mism=0;tested=0
    for _ in range(150):
        n=rnd.randint(1,30); m=rnd.randint(0,20); rects=[]
        for _ in range(m):
            x1=rnd.randint(1,n); x2=rnd.randint(x1,n); y1=rnd.randint(1,n); y2=rnd.randint(y1,n)
            rects.append((x1,y1,x2,y2))
        inp=f"{n} {m}\n"+"".join(f"{x1} {y1} {x2} {y2}\n" for x1,y1,x2,y2 in rects)
        exp=ok3397(n,rects); o,rc,_=run(e,inp); tested+=1
        if o!=exp: mism+=1
    R["P3397_smtoxvvs"].update({"random_tested":tested,"mismatch":mism})

# =====================================================================
# 10. P1116 vt4bqm6v —— 车厢重组（归并排序逆序对）
# =====================================================================
S1116 = r"""
#include<bits/stdc++.h>
using namespace std;
long long t[500005],ans = 0;
void merge(int a[],int l,int r){
    if(l == r) return;
    int mid = (l+r)/2;
    merge(a,l,mid);
    merge(a,mid+1,r);
    int i = l,j = mid + 1,k = l;
    while(i<=mid&&j<=r){
        if(a[i]>a[j]){ t[k++] = a[j++]; ans += mid - i + 1; }
        else t[k++] = a[i++];
    }
    while(i<=mid) t[k++] = a[i++];
    while(j<=r) t[k++] = a[j++];
    for(i = l;i<=r;i++) a[i] = t[i];
}
int main(){
    int n,a[500005];
    cin>>n;
    for(int i = 1;i<=n;i++) cin>>a[i];
    merge(a,1,n);
    cout<<ans<<endl;
    return 0;
}
"""
def ok1116(arr): return str(sum(1 for i in range(len(arr)) for j in range(i+1,len(arr)) if arr[i]>arr[j]))
e,err,ce=cc("s1116",S1116)
R["P1116_vt4bqm6v"]={"compile_error":err}
if not ce:
    cases=[]
    for arr in [[1],[1,2,3],[3,2,1],[4,3,2,1],[2,1,3],[5,1,4,2,3],[1,1,1]]:
        inp=f"{len(arr)}\n"+" ".join(map(str,arr))+"\n"
        exp=ok1116(arr); o,rc,_=run(e,inp)
        cases.append({"input":" ".join(map(str,arr)),"expected":exp,"actual":o.strip(),"hacked":o.strip()!=exp})
    R["P1116_vt4bqm6v"]["cases"]=cases
    rnd=random.Random(20261122);mism=0;tested=0
    for _ in range(200):
        n=rnd.randint(1,60); arr=list(range(1,n+1)); rnd.shuffle(arr)
        inp=f"{n}\n"+" ".join(map(str,arr))+"\n"
        exp=ok1116(arr); o,rc,_=run(e,inp); tested+=1
        if o.strip()!=exp: mism+=1
    R["P1116_vt4bqm6v"].update({"random_tested":tested,"mismatch":mism})

# =====================================================================
# 11. P2089 vgwp3k30 —— 烤鸡（10 层枚举）
# =====================================================================
S2089 = r"""
#include<bits/stdc++.h>
using namespace std;
int zl[50000][10];
int main(){
    int n,ans=0;
    cin>>n;
    for (int a=1;a<=3;a++){
    for (int b=1;b<=3;b++){
    for (int c=1;c<=3;c++){
    for (int d=1;d<=3;d++){
    for (int e=1;e<=3;e++){
    for (int f=1;f<=3;f++){
    for (int g=1;g<=3;g++){
    for (int h=1;h<=3;h++){
    for  (int i=1;i<=3;i++){
    for  (int j=1;j<=3;j++){
        if (a+b+c+d+e+f+g+h+i+j==n) {
            ans++;
            zl[ans][0]=a;zl[ans][1]=b; zl[ans][2]=c;zl[ans][3]=d;
            zl[ans][4]=e;zl[ans][5]=f;zl[ans][6]=g;zl[ans][7]=h;
            zl[ans][8]=i;zl[ans][9]=j;
        }
    } } } } } } } } } }
    cout<<ans<<endl;
    for (int i=1;i<=ans;i++){
        cout<<zl[i][0]<<" "; cout<<zl[i][1]<<" "; cout<<zl[i][2]<<" ";
        cout<<zl[i][3]<<" "; cout<<zl[i][4]<<" "; cout<<zl[i][5]<<" ";
        cout<<zl[i][6]<<" "; cout<<zl[i][7]<<" "; cout<<zl[i][8]<<" ";
        cout<<zl[i][9]<<endl;
    }
    return 0;
}
"""
def ok2089(n):
    sols=[p for p in itertools.product([1,2,3],repeat=10) if sum(p)==n]
    out=[str(len(sols))]
    for p in sols: out.append(" ".join(map(str,p)))
    return "\n".join(out)+"\n"
e,err,ce=cc("s2089",S2089)
R["P2089_vgwp3k30"]={"compile_error":err}
if not ce:
    cases=[]
    for n in [10,11,12,20,29,30,9,31,5000,1]:
        o,rc,_=run(e,f"{n}\n",t=60); exp=ok2089(n)
        cases.append({"input":n,"expected_first_line":exp.split("\n")[0],"actual_first_line":o.split("\n")[0],
                      "full_match":o==exp,"hacked":o!=exp})
    R["P2089_vgwp3k30"]["cases"]=cases
    # 最大方案数（n=20）
    o,rc,_=run(e,"20\n",t=60)
    R["P2089_vgwp3k30"]["max_solutions"]={"n=20 方案数":o.split("\n")[0],"zl 行数":50000}

json.dump(R,open(os.path.join(BASE,"results.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=2)
print(json.dumps(R,ensure_ascii=False,indent=2))
