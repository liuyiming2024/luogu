// P1421 · 本地独立正确解（std）
// 已确认题面口径：0<=a<=1e4, 0<=b<=9；1.9 元/支，问 a 元 b 角能买几支。
// 关键：全部换算成「角」做整数除法，绝不用 double 反复减 1.9。
// 已知 hack 对照：7 6 -> 4、19 0 -> 10（double 版在 19 角整数倍处少买一支）。
#include <bits/stdc++.h>
using namespace std;
int main(){
    long long a,b;
    if(!(cin>>a>>b)) return 0;
    cout << (a*10+b)/19 << '\n';
    return 0;
}
