// P1037 产生数 · std：Floyd 传递闭包求每位可达数字数，__int128 累乘输出。
// 题面逐字「规则的右部不能为零」；n<10^30，首位不会变成 0。
#include <bits/stdc++.h>
using namespace std;
string out128(__int128 v){
    if(v==0) return "0";
    string s; while(v>0){ s+=char('0'+v%10); v/=10; }
    reverse(s.begin(),s.end()); return s;
}
int main(){
    string n; int k; if(!(cin>>n>>k)) return 0;
    bool reach[10][10]={0};
    for(int i=0;i<10;i++) reach[i][i]=1;
    for(int q=0;q<k;q++){ int a,b; cin>>a>>b; reach[a][b]=1; }
    for(int m=0;m<10;m++)for(int i=0;i<10;i++)for(int j=0;j<10;j++)
        if(reach[i][m]&&reach[m][j]) reach[i][j]=1;
    __int128 ans=1;
    for(char c:n){ int cnt=0; for(int j=0;j<10;j++) cnt+=reach[c-'0'][j]; ans*=cnt; }
    cout<<out128(ans)<<'\n'; return 0;
}
