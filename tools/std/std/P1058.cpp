// P1058 立体图 · std（逐 cube 正向绘制到画布）：
// 坐标由题面「(m,1) 格最底积木左下角为整图最左下角」+ 三种相邻图示反推：
//   r(i,j,k) = 2*(i-1) + 3 - 3*(k-1)     （k 自底向上；越高越靠上）
//   c(i,j,k) = 4*(j-1) + 2*(m-i)
// 题面 tile 中「cube 外部空白」用背景 '.' 表示、「cube 内部空白」保留空格；
// 绘制时跳过 '.'（背景不覆盖已画内容），写入空格与实体字符；最后按包围框输出。
#include <bits/stdc++.h>
using namespace std;
const char* TILE[6] = {"..+---+", "./   /|", "+---+ |",
                       "|   | +", "|   |/.", "+---+.."};
int main(){
    int m,n; if(!(cin>>m>>n)) return 0;
    vector<vector<int>> h(m+1, vector<int>(n+1,0));
    for(int i=1;i<=m;i++) for(int j=1;j<=n;j++) cin>>h[i][j];
    long long minR=4e18,minC=4e18,maxR=-4e18,maxC=-4e18;
    for(int i=1;i<=m;i++) for(int j=1;j<=n;j++) for(int k=1;k<=h[i][j];k++){
        long long r=2LL*(i-1)+3-3LL*(k-1), c=4LL*(j-1)+2LL*(m-i);
        minR=min(minR,r); minC=min(minC,c);
        maxR=max(maxR,r+5); maxC=max(maxC,c+6);
    }
    int K=(int)(maxR-minR+1), L=(int)(maxC-minC+1);
    vector<string> cv(K, string(L,'.'));
    for(int i=1;i<=m;i++) for(int j=1;j<=n;j++) for(int k=1;k<=h[i][j];k++){
        long long r=2LL*(i-1)+3-3LL*(k-1)-(minR), c=4LL*(j-1)+2LL*(m-i)-(minC);
        for(int dr=0;dr<6;dr++) for(int dc=0;dc<7;dc++){
            char ch=TILE[dr][dc];
            if(ch!='.') cv[(int)r+dr][(int)c+dc]=ch;
        }
    }
    for(auto&s:cv) cout<<s<<"\n";
    return 0;
}
