// 等价：同为 O(n)，写法不同，落在波动带内应「不收」。
#include <bits/stdc++.h>
using namespace std;
int main(){ long long n; if(!(cin>>n)) return 0; long long s=0;
  for(long long i=0;i<n;i++) s+=n-i; cout<<s<<'\n'; return 0; }
