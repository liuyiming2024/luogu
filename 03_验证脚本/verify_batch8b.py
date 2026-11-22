#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 8 批补充：P1098 zcy00qo9（逐字取回的展开段拼装）"""
import os,json,random,subprocess
B="/data/workspace/luogu_hack/build/r8"
R={}

ZCY = r"""
#include<bits/stdc++.h>
using namespace std;
int d[101],top;
int p1,p2,p3;
char a[101];
int main(){
 scanf("%d%d%d\n",&p1,&p2,&p3);
 scanf("%s",a);
 int lena=strlen(a);
 for(register int i=0;i<lena;i++){
  if(a[i]=='-'&&(a[i+1]=='-'||a[i-1]=='-')){ putchar('-'); continue; }
  if(a[i]=='-'&&((a[i-1]>='0'&&a[i-1]<='9'&&a[i+1]>='a'&&a[i+1]<='z')||(a[i+1]>='0'&&a[i+1]<='9'&&a[i-1]>='a'&&a[i-1]<='z'))){ putchar('-'); continue; }
  if(a[i]=='-'&&a[i+1]<a[i-1]){ putchar('-'); continue; }
  if(a[i]=='-'&&i==0){ putchar('-'); continue; }
  if(a[i]!='-'){ putchar(a[i]); continue; }
  if(a[i]=='-'&&a[i-1]+1==a[i+1])continue;
  if(a[i]=='-'&&a[i-1]==a[i+1]){ putchar('-'); continue; }
  if(a[i]=='-'&&((a[i-1]<='z'&&a[i-1]>='a'&&a[i+1]>='a'&&a[i-1]<='z')||(a[i-1]<='9'&&a[i-1]>='0'&&a[i+1]<='9'&&a[i+1]>='0'))){
   if(p1==3)
    for(register int j=a[i-1]+1;j<=a[i+1]-1;j++)
     for(register int k=1;k<=p2;k++) putchar('*');
   else if(p1==2){
    if(a[i-1]>='a'&&a[i+1]<='z'){
     if(p3==1)
      for(register int j=a[i-1]+1;j<=a[i+1]-1;j++)
       for(register int k=1;k<=p2;k++) putchar(j-'a'+'A');
     else if(p3==2)
      for(register int j=a[i+1]-1;j>a[i-1];j--)
       for(register int k=1;k<=p2;k++) putchar(j-'a'+'A');
    }
    else
     for(register int j=a[i-1]+1;j<=a[i+1]-1;j++)
      for(register int k=1;k<=p2;k++) putchar(j);
   }
   else if(p1==1){
    if(p3==1)
     for(register int j=a[i-1]+1;j<=a[i+1]-1;j++)
      for(register int k=1;k<=p2;k++) putchar(j);
    else if(p3==2)
     for(register int j=a[i+1]-1;j>a[i-1];j--)
      for(register int k=1;k<=p2;k++) putchar(j);
   }
   continue;
  }
 }
 return 0;
}
"""
# 修复版：仅给 p1==2 的数字分支补 p3==2 逆序（补分支）
FIX = ZCY.replace(
"""    else
     for(register int j=a[i-1]+1;j<=a[i+1]-1;j++)
      for(register int k=1;k<=p2;k++) putchar(j);
""",
"""    else if(p3==2)
     for(register int j=a[i+1]-1;j>a[i-1];j--)
      for(register int k=1;k<=p2;k++) putchar(j);
    else
     for(register int j=a[i-1]+1;j<=a[i+1]-1;j++)
      for(register int k=1;k<=p2;k++) putchar(j);
""")

def cc(name,src):
    p=f"{B}/{name}.cpp";e=f"{B}/{name}"
    open(p,"w",encoding="utf-8").write(src)
    r=subprocess.run(["g++","-std=c++17","-O2","-o",e,p],capture_output=True,text=True)
    return e,(r.stderr[:500] if r.returncode else ""),r.returncode
def run(e,inp,t=25):
    p=subprocess.run([e],input=inp,capture_output=True,text=True,timeout=t)
    return p.stdout,p.returncode

def ok1098(s,p1,p2,p3):
    out=[];L=len(s)
    for i,ch in enumerate(s):
        if ch!='-': out.append(ch); continue
        if i==0 or i==L-1: out.append('-'); continue
        a,b=s[i-1],s[i+1]
        sd=('0'<=a<='9') and ('0'<=b<='9')
        sa=('a'<=a<='z') and ('a'<=b<='z')
        if not(sd or sa): out.append('-'); continue
        if b<=a: out.append('-'); continue
        cs=[chr(c) for c in range(ord(a)+1,ord(b))]
        if p1==3: cs=['*']*len(cs)
        elif p1==2 and sa: cs=[c.upper() for c in cs]
        if p3==2: cs=list(reversed(cs))
        out.append(''.join(c*p2 for c in cs))
    return ''.join(out)

for tag,src in [("orig",ZCY),("fix",FIX)]:
    e,err,ce=cc("f_zcy_"+tag,src)
    R[tag]={"compile_error":err}

if all(v.get("compile_error")=="" for v in R.values()):
    fixed=[("官方样例1",1,2,1,"abcs-w1234-9s-4zz"),
           ("官方样例2",2,3,2,"a-d-d"),
           ("p1=1 p3=2 数字",1,2,2,"1-5"),
           ("p1=2 p3=2 数字",2,2,2,"1-5"),
           ("p1=2 p3=1 数字",2,2,1,"1-5"),
           ("p1=2 p3=2 字母",2,2,2,"a-d"),
           ("p1=3 p3=2 数字",3,2,2,"1-5"),
           ("后继",1,2,1,"d-e"),
           ("连续减号",1,2,1,"a--d"),
           ("长度1",1,2,1,"a")]
    cases=[]
    for label,p1,p2,p3,s in fixed:
        exp=ok1098(s,p1,p2,p3);inp=f"{p1} {p2} {p3}\n{s}\n"
        o,rc=run(f"{B}/f_zcy_orig",inp);w,rc2=run(f"{B}/f_zcy_fix",inp)
        cases.append({"label":label,"input":f"{p1} {p2} {p3} / {s}","expected":exp,"actual":o,"fix_actual":w,"hacked":o!=exp})
    R["cases"]=cases
    rnd=random.Random(20261121);stats={t:{"tested":0,"mismatch":0,"examples":[]} for t in ["orig","fix"]}
    alpha="abcdefghijklmnopqrstuvwxyz0123456789-"
    for _ in range(400):
        p1=rnd.randint(1,3);p2=rnd.randint(1,8);p3=rnd.randint(1,2)
        L=rnd.randint(1,30);s="".join(rnd.choice(alpha) for _ in range(L))
        exp=ok1098(s,p1,p2,p3);inp=f"{p1} {p2} {p3}\n{s}\n"
        for tag in ["orig","fix"]:
            o,rc=run(f"{B}/f_zcy_{tag}",inp)
            stats[tag]["tested"]+=1
            if o!=exp:
                stats[tag]["mismatch"]+=1
                if len(stats[tag]["examples"])<4:stats[tag]["examples"].append({"input":inp.strip().replace("\n"," / "),"expected":exp,"actual":o})
    R["random"]=stats

json.dump(R,open(f"{B}/results_extra.json","w",encoding="utf-8"),ensure_ascii=False,indent=2)
print(json.dumps(R,ensure_ascii=False,indent=2))
