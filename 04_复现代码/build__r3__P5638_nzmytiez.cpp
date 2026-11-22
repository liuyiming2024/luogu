
#include <bits/stdc++.h>
using namespace std;
int n, k, a, b;
long long cxk[1000010], ans, maxx, ans2;
int main(){
 ios::sync_with_stdio(false);
 cin >> n >> k;
 for (int i = 1; i <= n - 1; i++) cin >> cxk[i], ans += cxk[i];
 a = 0, b = a + k;
 for (int i = a; i < b; i++) ans2 += cxk[i];
 for (int i = 1; i <= n - k; i++) {
  ans2 = ans2 + cxk[b] - cxk[a];
  maxx = max(maxx, ans2);
  a++, b++;
 }
 cout << ans - maxx;
 return 0;
}
