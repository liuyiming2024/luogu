
#include<bits/stdc++.h>
#define N 1010
int n,m; int map[N][N],d[N][N];
struct node { int x1,y1,x2,y2; };
node a[N];
namespace WalkerV {
    void Read() {
		scanf("%d%d",&n,&m);
		for(int i=1;i<=m;i++) scanf("%d%d%d%d",&a[i].x1,&a[i].y1,&a[i].x2,&a[i].y2);
		return;
    }
    void Solve() {
		for(int i=1;i<=m;i++) {
			d[a[i].x1][a[i].y1]++;
			d[a[i].x2+1][a[i].y1]--;
			d[a[i].x1][a[i].y2+1]--;
			d[a[i].x2+1][a[i].y2+1]++;
		}
		for(int i=1;i<=n;i++)
			for(int j=1;j<=n;j++)
				map[i][j]=map[i][j-1]+map[i-1][j]-map[i-1][j-1]+d[i][j];
		return;
    }
    void Print() {
		for(int i=1;i<=n;i++)
			for(int j=1;j<=n;j++)
				printf("%d%c",map[i][j],j==n?'\n':' ');
		return;
    }
}
int main(){ WalkerV::Read(); WalkerV::Solve(); WalkerV::Print(); return 0; }
