
#include<bits/stdc++.h>
using namespace std;
int zl[50000][10];
int main(){
    int n,ans=0;
    cin>>n;
    for (int a=1;a<=3;a++){
    for (int b=1;b<=3;b++){
    for (int c=1;c<=3;c++){
    for (int d=1;d<=3;d++){
    for (int e=1;e<=3;e++){
    for (int f=1;f<=3;f++){
    for (int g=1;g<=3;g++){
    for (int h=1;h<=3;h++){
    for  (int i=1;i<=3;i++){
    for  (int j=1;j<=3;j++){
        if (a+b+c+d+e+f+g+h+i+j==n) {
            ans++;
            zl[ans][0]=a;zl[ans][1]=b; zl[ans][2]=c;zl[ans][3]=d;
            zl[ans][4]=e;zl[ans][5]=f;zl[ans][6]=g;zl[ans][7]=h;
            zl[ans][8]=i;zl[ans][9]=j;
        }
    } } } } } } } } } }
    cout<<ans<<endl;
    for (int i=1;i<=ans;i++){
        cout<<zl[i][0]<<" "; cout<<zl[i][1]<<" "; cout<<zl[i][2]<<" ";
        cout<<zl[i][3]<<" "; cout<<zl[i][4]<<" "; cout<<zl[i][5]<<" ";
        cout<<zl[i][6]<<" "; cout<<zl[i][7]<<" "; cout<<zl[i][8]<<" ";
        cout<<zl[i][9]<<endl;
    }
    return 0;
}
