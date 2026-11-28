// P1024 std：0.01 步长扫符号变化 + 60 次二分，2 位小数。
#include <bits/stdc++.h>
using namespace std;double a,b,c,d;double f(double x){return ((a*x+b)*x+c)*x+d;}
int main(){if(!(cin>>a>>b>>c>>d))return 0;vector<double> r;
 for(int xi=-10000;xi<10000;xi++){double l=xi/100.0,rr=(xi+1)/100.0;
  if(fabs(f(l))<1e-7){r.push_back(l);continue;}
  if(f(l)*f(rr)<0){for(int it=0;it<60;it++){double m=(l+rr)/2;if(f(l)*f(m)<=0)rr=m;else l=m;}r.push_back((l+rr)/2);}}
 vector<double> u;for(double v:r)if(u.empty()||v-u.back()>0.5)u.push_back(v);
 while(u.size()<3)u.push_back(0);printf("%.2f %.2f %.2f\n",u[0],u[1],u[2]);return 0;}
