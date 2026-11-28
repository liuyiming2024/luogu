// P1055 ISBN 号码 · std：逐字符扫描，跳过 '-' 累加前 9 位加权和，识别码 X 视为 10。
#include <bits/stdc++.h>
using namespace std;
int main(){
    string s; if(!(cin>>s)) return 0;
    int sum=0, cnt=0;
    for(char c:s){
        if(c=='-') continue;
        if(cnt<9){ sum+=(c-'0')*(cnt+1); cnt++; }
    }
    int chk = (s.back()=='X') ? 10 : (s.back()-'0');
    if(sum%11==chk){ cout<<"Right\n"; return 0; }
    string out=s.substr(0,12);
    int r=sum%11;
    out += (r==10) ? 'X' : char('0'+r);
    cout<<out<<'\n'; return 0;
}
