// 工单示例：scanf/printf 版，正确但无明显优势（应「等价不收」）
#include <cstdio>
int main(){ long long a,b; if(scanf("%lld%lld",&a,&b)!=2) return 0;
  printf("%lld\n",a+b); return 0; }
