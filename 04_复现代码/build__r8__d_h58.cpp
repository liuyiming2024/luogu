
#include<bits/stdc++.h>
#define unique2648 return
#define code 0
using namespace std;
int main(){
 int n,x; cin >> n;
 for (int i = n;i >= 0;i--){ cin >> x;
  if (x!=0){
   if (x>0&&i!=n){ cout << "+"; }
   if (abs(x)!=1||i==0){ cout << x; }
   else if(x==-1) cout << "-";
   if (i>=2) cout << "x^" << i;
   else if (i==1) cout << "x";
  }
 }
 unique2648 code;
}
