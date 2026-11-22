#include <bits/stdc++.h>
#define int long long
using namespace std;
int h[300 + 9];
signed main() {
    int n; cin >> n;
    for (int i = 1; i <= n; i ++) cin >> h[i];
    sort(h + 1, h + n + 1);
    int lt = 1, rt = n, t = 0, now = 0;
    for (int i = 1; i <= n; i ++) {
        if (i % 2 != 0) {
            t += (now - h[rt]) * (now - h[rt]);
            now = h[rt]; rt --;
        } else {
            t += (now - h[lt]) * (now - h[lt]);
            now = h[lt]; lt ++;
        }
    }
    cout << t;
    return 0;
}
