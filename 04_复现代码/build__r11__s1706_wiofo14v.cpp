
#include<bits/stdc++.h>
using namespace std;
int arr[15];
int vis[15];
int n;
void dfs(int k){
    if (k>n){
        for (int i=1;i<=n;i++){ cout << setw(5) << arr[i]; }
        puts("");
        return;
    }
    for (int i=1;i<=n;i++){
        if (vis[i]!=1){ arr[k]=i; vis[i]=1; dfs(k+1); vis[i]=0; }
    }
}
int main(){ scanf("%d",&n); dfs(1); return 0; }
