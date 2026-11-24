#include<iostream>
using namespace std;
int main(){
 int score[5][5];
 score[0][0]=0;
 score[0][1]=1;
 score[0][2]=1;
 score[0][3]=1;
 score[0][4]=-1;
 score[1][0]=1;
 score[1][1]=0;
 score[1][2]=-1;
 score[1][3]=1;
 score[1][4]=-1;
 score[2][0]=-1;
 score[2][1]=1;
 score[2][2]=0;
 score[2][3]=-1;
 score[2][4]=1;
 score[3][0]=-1;
 score[3][1]=-1;
 score[3][2]=1;
 score[3][3]=0;
 score[3][4]=1;
 score[4][0]=1;
 score[4][1]=1;
 score[4][2]=-1;
 score[4][3]=-1;
 score[4][4]=0;
 int n,m,k; int ans=0; int bns=0; cin>>n>>m>>k;
 int a[m+1],b[k+1];
 for(int i=1;i<=m;i++) cin>>a[i];
 for(int i=1;i<=k;i++) cin>>b[i];
 int anum=1; int bnum=1;
 for(int i=1;i<=n;i++){
   if(score[a[anum]][b[bnum]]==1) ans++;
   else if(score[a[anum]][b[bnum]]==-1) bns++;
   anum++; bnum++;
   if(anum>m){ anum=1; }
   if(bnum>k){ bnum=1; }
 }
 cout<<ans<<" "<<bns; return 0; }
