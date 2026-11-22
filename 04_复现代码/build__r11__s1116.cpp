
#include<bits/stdc++.h>
using namespace std;
long long t[500005],ans = 0;
void merge(int a[],int l,int r){
    if(l == r) return;
    int mid = (l+r)/2;
    merge(a,l,mid);
    merge(a,mid+1,r);
    int i = l,j = mid + 1,k = l;
    while(i<=mid&&j<=r){
        if(a[i]>a[j]){ t[k++] = a[j++]; ans += mid - i + 1; }
        else t[k++] = a[i++];
    }
    while(i<=mid) t[k++] = a[i++];
    while(j<=r) t[k++] = a[j++];
    for(i = l;i<=r;i++) a[i] = t[i];
}
int main(){
    int n,a[500005];
    cin>>n;
    for(int i = 1;i<=n;i++) cin>>a[i];
    merge(a,1,n);
    cout<<ans<<endl;
    return 0;
}
