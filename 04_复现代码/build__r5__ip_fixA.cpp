
#include <bits/stdc++.h>
using namespace std;
const int inf = 1061109567;
const int N = 1e4 + 10;
int n, m, a[N];
int dp[310][10011];
signed main(){
 cin >> n >> m;
 for (int i = 1; i <= n; i++) cin >>a[i];
 dp[0][0] = 1;
 for (int i = 1; i <= n; i++){
     dp[i][0] = 1;
     for (int j = m; j >= 1; -- j) {
         if (j >= a[i]) dp[i][j] = dp[i - 1][j - a[i]] + dp[i - 1][j];
         else dp[i][j] = dp[i - 1][j];
     }
 }
 cout << dp[n][m] << endl;
 return 0;
}
