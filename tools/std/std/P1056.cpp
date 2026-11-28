// P1056 排座椅 · std（贪心）：横/纵通道各自按「能隔开的交头接耳对数」降序取前 K/L 条，
// 再按编号升序输出。题面保证最优方案唯一。
#include <bits/stdc++.h>
using namespace std;
int main(){
    int M,N,K,L,D; if(!(cin>>M>>N>>K>>L>>D)) return 0;
    vector<int> row(M,0), col(N,0);
    for(int q=0;q<D;q++){
        int x,y,p,z; cin>>x>>y>>p>>z;
        if(x==p) col[min(y,z)]++;
        else row[min(x,p)]++;
    }
    vector<int> ri(M-1), ci(N-1);
    iota(ri.begin(),ri.end(),1); iota(ci.begin(),ci.end(),1);
    sort(ri.begin(),ri.end(),[&](int a,int b){ return row[a]!=row[b] ? row[a]>row[b] : a<b; });
    sort(ci.begin(),ci.end(),[&](int a,int b){ return col[a]!=col[b] ? col[a]>col[b] : a<b; });
    vector<int> A(ri.begin(),ri.begin()+K), B(ci.begin(),ci.begin()+L);
    sort(A.begin(),A.end()); sort(B.begin(),B.end());
    for(size_t i=0;i<A.size();i++){ if(i) cout<<" "; cout<<A[i]; } cout<<"\n";
    for(size_t i=0;i<B.size();i++){ if(i) cout<<" "; cout<<B[i]; } cout<<"\n";
    return 0;
}
