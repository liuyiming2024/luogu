// 明显不优：正确但多跑 3 倍 volatile 循环。
#include <bits/stdc++.h>
using namespace std;
int main(){ long long n; if(!(cin>>n)) return 0; long long s=0;
  volatile long long t=0;
  for(long long i=1;i<=n;i++){ s+=i; t+=i; t+=i; t+=i; }
  cout<<s<<'\n'; (void)t; return 0; }
