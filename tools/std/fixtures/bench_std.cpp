// 验证夹具（不进正式题库）：当前已迁入的朴素 std，O(n) 求和。
#include <bits/stdc++.h>
using namespace std;
int main(){ long long n; if(!(cin>>n)) return 0; long long s=0;
  for(long long i=1;i<=n;i++) s+=i; cout<<s<<'\n'; return 0; }
