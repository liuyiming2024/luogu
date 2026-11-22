
#include<stdio.h>
int w_time(int sh,int sm,int eh,int em)
{
	int startm,endm,usem;
	startm=sh*60+sm;
	endm=eh*60+em;
	usem=endm-startm;
	return usem;
}
int main()
{
	int sh,sm,eh,em,uset,useh,usem;
	scanf("%d%d%d%d",&sh,&sm,&eh,&em);
	uset=w_time(sh,sm,eh,em);
	useh=uset/60;
	usem=uset%60;
	printf("%d %d",useh,usem);
	return 0;
}
