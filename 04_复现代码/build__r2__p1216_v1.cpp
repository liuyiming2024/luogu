#include <iostream>
using namespace std;
const int MR(1001);
int map[MR][MR];
int dp[MR][MR];
int n;
inline int dmax(const int& a,const int& b){ return (a>b ? a : b); }
int main(){
    cin >> n;
    for(int i(1);i<=n;++i)
        for(int j(1);j<=i;++j)
            cin >> map[i][j];
    for(int i(1);i<=n;++i)    dp[n][i] = map[n][i];
    for(int i(n-1);i>0;--i)
        for(int j(1);j<=n;++j)
            dp[i][j] = map[i][j] + dmax(dp[i+1][j], dp[i+1][j+1]);
    cout << dp[1][1];
    return 0;
}
