#include<bits/stdc++.h>
using namespace std;
int main(){
    int n,s=0,t;
    scanf("%d",&n);
    for(int i=1;i<=n;i++){ scanf("%d",&t); s=s^t; }
    printf("%d",s);
    return 0;
}
