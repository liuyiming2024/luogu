// P1421 朴素算法：不用除法，把钱换成角后一角一角累减 19，数能减几次。
#include <bits/stdc++.h>
using namespace std;
int main(){
    long long a,b; if(!(cin>>a>>b)) return 0;
    long long money = a*10 + b, cnt = 0;
    while(money >= 19){ money -= 19; cnt++; }
    cout<<cnt<<'\n'; return 0;
}
