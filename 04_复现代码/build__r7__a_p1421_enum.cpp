
#include <bits/stdc++.h>
using namespace std;
// 题解拼装版（逐字段）
int solve_sol(int A,int B){
    double a,b; int sum=0;
    a=A; b=B;
    b=b/10;
    a=a+b;
    while(a>=1.9){ a=a-1.9; sum++; }
    return sum;
}
// 独立正确解：全部换算成角，整数除法
int solve_ok(int A,int B){ return (A*10+B)/19; }
int main(){
    int total=0,bad=0; vector<string> ex;
    for(int A=0;A<=10000;A++) for(int B=0;B<=9;B++){
        total++;
        int s=solve_sol(A,B), o=solve_ok(A,B);
        if(s!=o){ bad++; if((int)ex.size()<12){ char buf[128]; sprintf(buf,"%d %d -> sol=%d ok=%d",A,B,s,o); ex.push_back(buf); } }
    }
    printf("A|total=%d|bad=%d\n",total,bad);
    for(auto &e:ex) printf("A|%s\n",e.c_str());
    return 0;
}
