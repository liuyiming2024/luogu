#include<bits/stdc++.h>
using namespace std;
string s;
int cnt=0;
int main(){
getline(cin,s);
for(char c:s)	if(c!=' '&&c!='\n') cnt++;
cout<<cnt;
return 0;
}
