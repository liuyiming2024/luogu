
#include<cstdio>
#include<algorithm>
#include<cstdlib>
#include<cstring>
#include<queue>
const int maxn=15,maxm=1010*2;
const int inf=0x3f3f3f3f;
const int seed=19260817,randtime=25000,swaptime=10;
struct KEDGE{ int x,y,w; bool isInMST; };
struct STAR{ int e,nxt,w; };
int n,m;
int map[maxn][maxn];
KEDGE kruskalEdge[maxm];
int father[maxn];
int head[maxn],starCnt=0;
STAR starEdge[maxm];
int vis1[maxn],vis2[maxn],kdep[maxn];
int kcnt=0,rcnt=0,cnt=0;
int ans=inf;
int rand(int l,int r){ return l + rand()%(r-l+1); }
bool compareLaw(const KEDGE &a,const KEDGE &b){ return a.w<b.w; }
int find(int x){ return father[x]==x?x:father[x]=find(father[x]); }
void unionx(int x,int y){ father[find(x)]=find(y); }
void add(int x,int y,int w){ starEdge[++starCnt]=(STAR){y,head[x],w}; head[x]=starCnt; }
void solve(int time){
 for(int i=1;i<=n;++i)father[i]=i;
 cnt=1,rcnt=0;
 memset(head,0,sizeof(head));
 memset(starEdge,0,sizeof(starEdge));
 for(int i=1;i<=kcnt;++i)kruskalEdge[i].isInMST=0;
 std::sort(kruskalEdge+1,kruskalEdge+kcnt+1,compareLaw);
 for(int i=1;i<=swaptime;++i)std::swap(kruskalEdge[rand(1,kcnt)],kruskalEdge[rand(1,kcnt)]);
 starCnt=0;
 for(int i=1;i<=kcnt;i++){
  int x=kruskalEdge[i].x,y=kruskalEdge[i].y;
  if(find(x)!=find(y)){
   unionx(x,y);
   kruskalEdge[i].isInMST=1;
   rcnt++;
   if(rcnt==n-1)break;
  }
 }
 for(int i=1;i<=kcnt;++i){
  if(kruskalEdge[i].isInMST){
   int x=kruskalEdge[i].x,y=kruskalEdge[i].y,w=kruskalEdge[i].w;
   add(x,y,w);
   add(y,x,w);
  }
 }
 for(int i=1;i<=n;++i){
  int res=0;
  memset(vis1,0,sizeof(vis1));
  memset(vis2,0,sizeof(vis2));
  memset(kdep,0,sizeof(kdep));
  std::queue<int>q1,q2;
  q1.push(i);
  kdep[i]=1;
  while(!q1.empty()){
   int pos=q1.front(); q1.pop();
   if(vis1[pos])continue;
   vis1[pos]=1;
   for(int j=head[pos];j;j=starEdge[j].nxt){
    int to=starEdge[j].e;
    if(!vis1[to]){ kdep[to]=kdep[pos]+1; q1.push(to); }
   }
  }
  q2.push(i);
  while(!q2.empty()){
   int pos=q2.front(); q2.pop();
   if(vis2[pos])continue;
   vis2[pos]=1;
   for(int j=head[pos];j;j=starEdge[j].nxt){
    int to=starEdge[j].e;
    if(!vis2[to]){ res+=starEdge[j].w*kdep[pos]; q2.push(to); }
   }
  }
  ans=std::min(ans,res);
 }
}
int main(){
 memset(map,0x3f,sizeof(map));
 srand(seed);
 scanf("%d%d",&n,&m);
 if(n==1&&m==0){ printf("0"); return 0; }
 for(int i=1;i<=m;++i){
  int u,v,w;
  scanf("%d%d%d",&u,&v,&w);
  map[u][v]=std::min(map[u][v],w);
  map[v][u]=std::min(map[v][u],w);
 }
 for(int i=1;i<=n;++i){
  for(int j=i;j<=n;++j){
   if(map[i][j]!=inf) kruskalEdge[++kcnt]=(KEDGE){i,j,map[i][j],0};
  }
 }
 for(int i=1;i<=randtime;++i)solve(i);
 printf("%d",ans);
 return 0;
}
