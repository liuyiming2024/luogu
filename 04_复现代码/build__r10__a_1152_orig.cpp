
#include <iostream>
#include <algorithm>
#include <cstdlib>
using namespace std;
int main() {
    int n, a[1005];
    cin >> n;
    if (n == 1) { cout << "Jolly"; return 0; }
    for (int i = 1; i <= n; i++) cin >> a[i];
    int dif[1005];
    for (int i = 1; i <= n - 1; i++) dif[i] = abs(a[i + 1] - a[i]);
    sort(dif + 1, dif + n);
    bool vis[10000005] = { 0 };
    for (int i = 1; i <= n - 1; i++) vis[dif[i]] = 1;
    for (int i = 1; i <= n - 1; i++) {
        if (!vis[i]) { cout << "Not jolly" << endl; return 0; }
    }
    cout << "Jolly" << endl;
    return 0;
}
