#include <bits/stdc++.h>
using namespace std;
int L,R,mid; double target,dist,per;
int sol(double tg,int mode){ // mode 0=原版,1=只改外层,2=两处都改
    L=0;R=INT_MAX;dist=0;per=2;target=tg;
    while(R>=L){
        mid=(int)(((long long)L+R)/2); // 防溢出写法，仅用于复验
        for(int i=1;i<=mid;i++){
            dist+=per; per*=0.98;
            if(mode==2){ if(dist>=target) break; }
            else { if(dist>target) break; }
        }
        bool ge = (mode==0)? (dist>target) : (dist>=target);
        if(ge) R=mid-1; else L=mid+1;
        dist=0; per=2;
    }
    return L;
}
int ok(double s){ double d=0,p=2; int a=0; while(d<s-1e-12){d+=p;p*=0.98;a++;} return a; }
int main(){
    mt19937 rng(20261121); uniform_real_distribution<double> ud(0.01,99.9);
    int bad[3]={0,0,0};
    for(int t=0;t<200;t++){ double s=round(ud(rng)*1e6)/1e6; int e=ok(s);
        for(int m=0;m<3;m++) if(sol(s,m)!=e) bad[m]++;
    }
    printf("200组随机不一致数: 原版=%d 只改外层=%d 两处都改=%d\n",bad[0],bad[1],bad[2]);
    double part[8]; double d=2,p=2*0.98; part[0]=2;
    for(int k=1;k<8;k++){d+=p;p*=0.98;part[k]=d;}
    for(int k=0;k<8;k++){
        printf("s=%.10g 期望=%d 原版=%d 只改外层=%d 两处都改=%d\n",part[k],ok(part[k]),sol(part[k],0),sol(part[k],1),sol(part[k],2));
    }
    return 0;
}
