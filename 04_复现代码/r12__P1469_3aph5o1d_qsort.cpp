#include<bits/stdc++.h>
using namespace std;
int a[1000001];
int n;
void qsort_(int l,int r){
    int i=l,j=r,x=a[(l+r)/2];
    do{
        while(a[i]<x) i++;
        while(x<a[j]) j--;
        if(i<=j){ int y=a[i]; a[i]=a[j]; a[j]=y; i++; j--; }
    }while(i<=j);
    if(l<j) qsort_(l,j);
    if(i<r) qsort_(i,r);
}
int main(){
    scanf("%d",&n);
    for(int i=1;i<=n;i++) scanf("%d",&a[i]);
    qsort_(1,n);
    int i=1;
    while(i+1<=n && a[i]==a[i+1]) i+=2;
    printf("%d",a[i]);
    return 0;
}
