
#include <stdio.h>
int main(){
 int me=0,mom=0,spend,i;
 for(i=1;i<=12;i++){
  me+=300;
  scanf("%d",&spend);
  me-=spend;
  if(me<0){ me=-i; break; }
  mom+=me/100*100;
  me%=100;
 }
 if(me<0) printf("%d",me);
 else printf("%g", me+mom*1.2);
 return 0;
}
