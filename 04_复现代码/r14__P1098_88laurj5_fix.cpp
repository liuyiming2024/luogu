#include<bits/stdc++.h>
using namespace std;
int p1,p2,p3; char a[101];
int main() {
scanf("%d%d%d",&p1,&p2,&p3);
cin>>a;
for(int i=0;i<strlen(a);i++) {
if(a[i]!='-') { cout<<a[i]; continue; }
if(a[i-1]>='0'&&a[i-1]<='9'&&(a[i+1]<'0'||a[i+1]>'9')) { printf("-"); continue; }
if(a[i+1]>='0'&&a[i+1]<='9'&&(a[i-1]<'0'||a[i-1]>'9')) { printf("-"); continue; }
if(a[i-1]>=a[i+1]) { printf("-"); continue; }
if(a[i+1]=='-'||a[i-1]=='-') { printf("-"); continue; }
if(i==0) { printf("-"); continue; }
if(p1==3&&i!=0) { for(char j=a[i-1]+1;j<a[i+1];j++) for(int k=1;k<=p2;k++) printf("*"); continue; }
if(p3==1) {
if(p1==1) for(char j=a[i-1]+1;j<a[i+1];j++) for(int k=1;k<=p2;k++) cout<<char(j);
if(p1==2) for(char j=a[i-1]-31;j<a[i+1]-32;j++) for(int k=1;k<=p2;k++) { if((a[i+1]>='0'&&a[i+1]<='9')||(a[i-1]>='0'&&a[i-1]<='9')) cout<<char(j+32); else cout<<char(j); }
}
if(p3==2) {
if(p1==1) for(char j=a[i+1]-1;j>a[i-1];j--) for(int k=1;k<=p2;k++) cout<<char(j);
if(p1==2) for(char j=a[i+1]-33;j>a[i-1]-32;j--) for(int k=1;k<=p2;k++) { if((a[i+1]>='0'&&a[i+1]<='9')||(a[i-1]>='0'&&a[i-1]<='9')) cout<<char(j+32); else cout<<char(j); }
}
}
return 0;
}
