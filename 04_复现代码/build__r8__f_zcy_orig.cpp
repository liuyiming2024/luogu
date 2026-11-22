
#include<bits/stdc++.h>
using namespace std;
int d[101],top;
int p1,p2,p3;
char a[101];
int main(){
 scanf("%d%d%d\n",&p1,&p2,&p3);
 scanf("%s",a);
 int lena=strlen(a);
 for(register int i=0;i<lena;i++){
  if(a[i]=='-'&&(a[i+1]=='-'||a[i-1]=='-')){ putchar('-'); continue; }
  if(a[i]=='-'&&((a[i-1]>='0'&&a[i-1]<='9'&&a[i+1]>='a'&&a[i+1]<='z')||(a[i+1]>='0'&&a[i+1]<='9'&&a[i-1]>='a'&&a[i-1]<='z'))){ putchar('-'); continue; }
  if(a[i]=='-'&&a[i+1]<a[i-1]){ putchar('-'); continue; }
  if(a[i]=='-'&&i==0){ putchar('-'); continue; }
  if(a[i]!='-'){ putchar(a[i]); continue; }
  if(a[i]=='-'&&a[i-1]+1==a[i+1])continue;
  if(a[i]=='-'&&a[i-1]==a[i+1]){ putchar('-'); continue; }
  if(a[i]=='-'&&((a[i-1]<='z'&&a[i-1]>='a'&&a[i+1]>='a'&&a[i-1]<='z')||(a[i-1]<='9'&&a[i-1]>='0'&&a[i+1]<='9'&&a[i+1]>='0'))){
   if(p1==3)
    for(register int j=a[i-1]+1;j<=a[i+1]-1;j++)
     for(register int k=1;k<=p2;k++) putchar('*');
   else if(p1==2){
    if(a[i-1]>='a'&&a[i+1]<='z'){
     if(p3==1)
      for(register int j=a[i-1]+1;j<=a[i+1]-1;j++)
       for(register int k=1;k<=p2;k++) putchar(j-'a'+'A');
     else if(p3==2)
      for(register int j=a[i+1]-1;j>a[i-1];j--)
       for(register int k=1;k<=p2;k++) putchar(j-'a'+'A');
    }
    else
     for(register int j=a[i-1]+1;j<=a[i+1]-1;j++)
      for(register int k=1;k<=p2;k++) putchar(j);
   }
   else if(p1==1){
    if(p3==1)
     for(register int j=a[i-1]+1;j<=a[i+1]-1;j++)
      for(register int k=1;k<=p2;k++) putchar(j);
    else if(p3==2)
     for(register int j=a[i+1]-1;j>a[i-1];j--)
      for(register int k=1;k<=p2;k++) putchar(j);
   }
   continue;
  }
 }
 return 0;
}
