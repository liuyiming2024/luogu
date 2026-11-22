
#include <stdio.h>
#include <stdlib.h>
int time[1000000][2];
int cmp1(const void *a,const void *b){ return ((int*)a)[0]-((int*)b)[0]; }
int cmp2(const void *a,const void *b){ return ((int*)a)[1]-((int*)b)[1]; }
int main(){
 int n,flag,pos = 0,count = 1;
 int i,j;
 scanf("%d", &n);
 for(i = 0; i < n; i++){ scanf("%d %d", &time[i][0],&time[i][1]); }
 qsort(time,n,sizeof(int)*2,cmp1);
 qsort(time,n,sizeof(int)*2,cmp2);
 for(i = 1; i < n; i++){
  flag = 1;
  if((time[i][0]>=time[pos][0]&&time[i][1]<=time[pos][1]) ||
     (time[i][1]>time[pos][0]&&time[i][1]<=time[pos][1]) ||
     (time[i][0]>=time[pos][0]&&time[i][0]<time[pos][1]) ||
     (time[pos][0]>time[i][0]&&time[pos][1]<time[i][1])){
   flag = 0;
  }
  if(flag == 1){ pos = i; count++; }
 }
 printf("%d", count);
 return 0;
}
