#include <iostream>
#include <algorithm>
using namespace std;
const int Mn(1002);
int dp[Mn][Mn];
int main(){
    int n;
    cin >> n;
    for(int i(1);i<=n;++i)
        for(int j(1);j<=i;++j){
            int tn; cin >> tn;
            dp[i][j] = max(dp[i-1][j-1],dp[i-1][j]) + tn;
        }
    int max(0);
    for(int i(1);i<=n;++i)
    if(dp[n][i] > max) max = dp[n][i];
    cout << max;
    return 0;
}
