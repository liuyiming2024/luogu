// P1051 谁拿了最多奖学金 · std：逐行解析 + 五条条件直接累加，保持输入顺序取最早并列。
#include <bits/stdc++.h>
using namespace std;
int main(){
    int N; if(!(cin>>N)) return 0;
    string bestName; int best=-1; long long total=0;
    for(int i=0;i<N;i++){
        string name, leader, west;
        int avg, cls, papers;
        cin>>name>>avg>>cls>>leader>>west>>papers;
        int s=0;
        if(avg>80 && papers>=1) s+=8000;          // 院士
        if(avg>85 && cls>80) s+=4000;              // 五四
        if(avg>90) s+=2000;                        // 成绩优秀
        if(avg>85 && west=="Y") s+=1000;           // 西部
        if(cls>80 && leader=="Y") s+=850;          // 班级贡献
        total+=s;
        if(s>best){ best=s; bestName=name; }
    }
    cout<<bestName<<"\n"<<best<<"\n"<<total<<"\n"; return 0;
}
