
#include<bits/stdc++.h>
using namespace std;
char j;
long long int a,b,c,d,e,f,g,h,i,k,l;
int main(){
    scanf("%1d-%1d%1d%1d-%1d%1d%1d%1d%1d-%c",&a,&b,&c,&d,&e,&f,&g,&h,&i,&j);
    k=(a*1+b*2+c*3+d*4+e*5+f*6+g*7+h*8+i*9)%11;
    if(j=='X') l=10; else l=j-'0';
    if(k==l) cout<<"Right";
    else if(k==10) cout<<a<<"-"<<b<<c<<d<<"-"<<e<<f<<g<<h<<i<<"-X";
    else cout<<a<<"-"<<b<<c<<d<<"-"<<e<<f<<g<<h<<i<<"-"<<k;
    return 0;
}
