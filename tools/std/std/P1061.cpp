// P1061 Jam 的计数法 · std（逐位进位找下一个严格递增串，输出 5 个）：
// 从右往左找第一个可增大的位，增 1 后其右侧依次取最小可用值。
#include <bits/stdc++.h>
using namespace std;
int main(){
    int s,t,w; string cur;
    if(!(cin>>s>>t>>w)) return 0;
    cin>>cur;
    vector<int> d(w);
    for(int i=0;i<w;i++) d[i]=cur[i]-'a'+1;
    for(int step=0;step<5;step++){
        int pos=-1;
        for(int i=w-1;i>=0;i--){
            int lim = t-(w-1-i);              // 该位最大可取，保证右侧还能放下
            if(d[i]<lim){ pos=i; break; }
        }
        if(pos<0) break;
        d[pos]++;
        for(int i=pos+1;i<w;i++) d[i]=d[i-1]+1;
        string out;
        for(int i=0;i<w;i++) out+=char('a'+d[i]-1);
        cout<<out<<"\n";
    }
    return 0;
}
