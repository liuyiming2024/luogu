
#include<iostream>
#include<cstdio>
using namespace std;
int n,m,b[25+1][30000+5]={0},i,j,v[25+1],p[25+1];
int main(){
 scanf("%d %d",&n,&m);
 for(i=1;i<=m;i++){
     scanf("%d %d",&v[i],&p[i]);
     for(j=n;j>=1;j--){
         b[i][j]=b[i-1][j];
         if(j>=v[i]&&b[i-1][j-v[i]]+v[i]*p[i]>b[i][j])b[i][j]=b[i-1][j-v[i]]+v[i]*p[i];
     }
 }
 printf("%d",b[m][n]);
 return 0;
}
