// P1024 朴素：0.001 步长 + 线性插值，不用二分。
#include <bits/stdc++.h>
using namespace std;double a,b,c,d;double f(double x){return ((a*x+b)*x+c)*x+d;}
int main(){if(!(cin>>a>>b>>c>>d))return 0;vector<double> r;
 for(int xi=-100000;xi<100000;xi++){double l=xi/1000.0,rr=(xi+1)/1000.0,fl=f(l),fr=f(rr);
  if(fabs(fl)<1e-7){r.push_back(l);continue;}
  if(fl*fr<0){double t=fl/(fl-fr);r.push_back(l+t*(rr-l));}}
 vector<double> u;for(double v:r)if(u.empty()||v-u.back()>0.5)u.push_back(v);
 while(u.size()<3)u.push_back(0);printf("%.2f %.2f %.2f\n",u[0],u[1],u[2]);return 0;}
