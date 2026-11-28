// P1421 小玉买文具 · 本地独立正确解（std）
// 题面逐字（site/data/problems/P1421.json）：一只签字笔 1 元 9 角，钱 a 元 b 角；
// 0≤a≤10^4, 0≤b≤9；样例 10 3 → 5。答案 =(a*10+b)/19。
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
