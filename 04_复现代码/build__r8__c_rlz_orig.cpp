
#include<bits/stdc++.h>
using namespace std;
int n;
int a[36][18];
int f(int p,int s){
 int aa=0;
 if(p==n*2){ if(s!=0) return 0; else return 1; }
 if(a[p][s]!=0) return a[p][s];
 if(s>0) aa+=f(p+1,s-1);
 aa+=f(p+1,s+1);
 a[p][s]=aa;
 return a[p][s];
}
int main(){ cin>>n; cout<<f(0,0); return 0; }
