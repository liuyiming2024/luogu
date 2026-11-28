// P1035 级数求和 · std：long double 线性累加直到 S_n>k。
#include <bits/stdc++.h>
using namespace std;
int main(){
    int k; if(!(cin>>k)) return 0;
    long double s=0;
    for(long long n=1;;n++){
        s += 1.0L/n;
        if(s>k){ cout<<n<<'\n'; return 0; }
    }
}
