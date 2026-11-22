
#include <iostream>
#include <vector>
using namespace std;

int countPaths(int n, int m, int horse_x, int horse_y) {
    vector<vector<int>> dp(n+1, vector<int>(m+1, 0));
    dp[0][0] = 1;

    for (int i = 0; i <= n; i++) {
        for (int j = 0; j <= m; j++) {
            if ((i-2 == horse_x && j-1 == horse_y) || (i-1 == horse_x && j-2 == horse_y)) {
                dp[i][j] = 0;
            } else {
                dp[i][j] = (i > 0 ? dp[i-1][j] : 0) + (j > 0 ? dp[i][j-1] : 0);
            }
        }
    }

    return dp[n][m];
}

int main() {
    int n, m, horse_x, horse_y;
    cin >> n >> m >> horse_x >> horse_y;

    int paths = countPaths(n, m, horse_x, horse_y);
    cout << paths << endl;

    return 0;
}
