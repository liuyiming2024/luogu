// P1045 麦森数 · std（手写 500 位十进制高精度 + 快速幂取模 10^500）：
// 位数 = floor(P*log10(2))+1；最后 500 位 = (2^P mod 10^500) - 1，高位补 0 分 10 行输出。
#include <bits/stdc++.h>
using namespace std;
const int D=500;
typedef array<int,D> Big;
Big one(){ Big x{}; x.fill(0); x[0]=1; return x; }
Big mul(const Big&a,const Big&b){
    Big c{}; c.fill(0);
    for(int i=0;i<D;i++){
        if(!a[i]) continue;
        long long carry=0;
        for(int j=0;i+j<D;j++){
            long long v=(long long)c[i+j]+(long long)a[i]*b[j]+carry;
            c[i+j]=(int)(v%10); carry=v/10;
        }
    }
    return c;
}
int main(){
    long long P; if(!(cin>>P)) return 0;
    Big r=one(), base=one(); base[0]=2;
    long long e=P;
    while(e>0){
        if(e&1) r=mul(r,base);
        base=mul(base,base);
        e>>=1;
    }
    // r = 2^P mod 10^500，减 1
    int pos=0;
    while(r[pos]==0 && pos<D-1) pos++;
    r[pos]-=1;
    for(int i=0;i<pos;i++) r[i]=9;
    // 位数
    int digits=(int)floor((long double)P*log10((long double)2))+1;
    cout<<digits<<"\n";
    string s; s.reserve(D);
    for(int i=D-1;i>=0;i--) s+=char('0'+r[i]);
    for(int i=0;i<D;i+=50) cout<<s.substr(i,50)<<"\n";
    return 0;
}
