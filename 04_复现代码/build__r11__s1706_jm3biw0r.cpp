
#include<bits/stdc++.h>
using namespace std;
int a[10]={0,1,2,3,4,5,6,7,8,9},n;
int main(){
    scanf("%d",&n);
    while(1){
        for(register int i=1;i<=n;++i) printf("%5d",a[i]);
        putchar('\n');
        if(!next_permutation(a+1,a+n+1)) break;
    }
    return 0;
}
