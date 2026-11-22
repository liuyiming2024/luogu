#include <bits/stdc++.h>
using namespace std;
int main(){
    int bad=0;
    for(int mom=0; mom<=3600; mom+=100){
        int a=mom; a*=1.2;                 // 题解写法
        int b=mom*6/5;                     // 整数正确写法
        double d=(double)mom*1.2;
        if(a!=b){ printf("mom=%4d  mom*=1.2 -> %4d   正确 %4d   double=%.17g\n",mom,a,b,d); bad++; }
    }
    printf("100倍数范围内不一致个数: %d\n",bad);
    // 再扫描所有 mom 0..3600（不只100倍数），看哪些会掉1
    int bad2=0, first=-1;
    for(int mom=0; mom<=3600; mom++){
        int a=mom; a*=1.2;
        if(a!=mom*6/5){ bad2++; if(first<0)first=mom; }
    }
    printf("全范围不一致 %d 个, 首个 mom=%d\n",bad2,first);
    return 0;
}
