
#include<bits/stdc++.h>
using namespace std;
int main(){
 int p1,p2,p3,l,k;
 string s; char x,y;
 cin>>p1>>p2>>p3;
 cin>>s;
 l=s.size();
 cout<<s[0];
 if(l==1) return 0;
 for(int t=1;t<l-1;++t){
  char a=s[t-1],b=s[t+1];
  if(p3==2){ x=b-1; y=a; k=-1; }
  else { x=a+1; y=b; k=1; }
  if(s[t]=='-'&&s[t-1]<s[t+1]){
   if(a>='a'&&a<='z'&&b>='a'&&b<='z'){
    if(p1==1){ for(char i=x;i<y&&k==1||i>y&&k==-1;i+=k){ for(int j=1;j<=p2;++j) cout<<char(i); } }
    else if(p1==2){ for(char i=x;i<y&&k==1||i>y&&k==-1;i+=k){ for(int j=1;j<=p2;++j) cout<<char(i-'a'+'A'); } }
    else if(p1==3){ for(char i=x;i<y&&k==1||i>y&&k==-1;i+=k){ for(int j=1;j<=p2;++j) cout<<"*"; } }
   }
   else if(a>='0'&&a<='9'&&b>='0'&&b<='9'){
    if(p1==3){ for(char i=x;i<y&&k==1||i>y&&k==-1;i+=k){ for(int j=1;j<=p2;++j) cout<<"*"; } }
    else { for(char i=x;i<y&&k==1||i>y&&k==-1;i+=k){ for(int j=1;j<=p2;++j) cout<<char(i); } }
   }
   else cout<<"-";
  }
  else cout<<s[t];
 }
 cout<<s[l-1];
 return 0;
}
