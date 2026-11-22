
#include<iostream>
#include<limits.h>
using namespace std;
int L,R=INT_MAX,mid; double target,dist,per=2;
int main(){ cin>>target;
 while(R>=L){ mid=(L+R)/2;
  for(int i=1;i<=mid;i++){ dist+=per; per*=0.98; if(dist>target) break; }
  if(dist>=target) R=mid-1; else L=mid+1;
  dist=0; per=2; }
 cout<<L; return 0; }
