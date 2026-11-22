import json,subprocess,itertools
from collections import Counter
B="/data/workspace/luogu_hack/build/r9"
def run(e,inp,t=10):
    try:
        p=subprocess.run([e],input=inp,capture_output=True,text=True,timeout=t)
        return p.stdout.strip(),p.returncode
    except subprocess.TimeoutExpired:
        return "<TIMEOUT>",-9
def ok(arr,c):
    cnt=Counter(arr); return sum(cnt[x+c] for x in arr)
R={}

# P1102：枚举小输入，找 rc==0 但输出错的最小反例，以及 rc!=0 的最小崩溃
worst=[];crash=[]
for n in range(1,6):
    for c in range(0,4):
        for arr in itertools.product(range(1,6),repeat=n):
            inp=f"{n} {c}\n"+" ".join(map(str,arr))+"\n"
            exp=str(ok(list(arr),c)); o,rc=run(f"{B}/x_1102_orig",inp,t=6)
            if rc!=0 and len(crash)<4: crash.append({"input":f"{n} {c} / "+" ".join(map(str,arr)),"expected":exp,"actual":o,"rc":rc})
            if rc==0 and o!=exp and len(worst)<6: worst.append({"input":f"{n} {c} / "+" ".join(map(str,arr)),"expected":exp,"actual":o})
R["P1102_minimal"]={"clean_wa":worst,"crash":crash}

# P1423：only_outer（改一处）在 200 组随机上复验
def ok1423(s):
    d=0.0;per=2.0;ans=0
    while d<s-1e-12:
        d+=per;per*=0.98;ans+=1
    return ans
import random
rnd=random.Random(20261121);bad=[]
for _ in range(200):
    s=round(rnd.uniform(0.01,99.9),6)
    o,rc=run(f"{B}/y_1423_only_outer",f"{s}\n",t=12)
    if o!=str(ok1423(s)) or rc!=0: bad.append({"s":s,"expected":ok1423(s),"actual":o,"rc":rc})
R["P1423_only_outer_random"]={"tested":200,"mismatch":len(bad),"examples":bad[:4]}
print(json.dumps(R,ensure_ascii=False,indent=2))
json.dump(R,open(f"{B}/results_extra2.json","w",encoding="utf-8"),ensure_ascii=False,indent=2)
