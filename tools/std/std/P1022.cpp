// P1022 std：符号解析移项 A*x+B=0，输出 3 位小数。
#include <bits/stdc++.h>
using namespace std;long long A=0,B=0;char var=0;
void parse(const string&s,int mul){int i=0,sign=1;
 while(i<(int)s.size()){char ch=s[i];if(ch=='+'){sign=1;i++;continue;}if(ch=='-'){sign=-1;i++;continue;}
  if(isdigit(ch)){long long num=0;while(i<(int)s.size()&&isdigit(s[i])){num=num*10+(s[i]-'0');i++;}
   if(i<(int)s.size()&&islower(s[i])){A+=(long long)mul*sign*num;var=s[i];i++;}else B+=(long long)mul*sign*num;}else i++;}}
int main(){string s;if(!(cin>>s))return 0;size_t eq=s.find('=');parse(s.substr(0,eq),1);parse(s.substr(eq+1),-1);
 double x=(double)(-B)/(double)A;if(fabs(x)<0.0005)x=0;printf("%c=%.3f\n",var,x);return 0;}
