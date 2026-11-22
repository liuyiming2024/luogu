#include<bits/stdc++.h>
using namespace std;
string n;
int main(){
	int cnt=0;
	getline(cin,n,'\n');
	for(int i=0;i<n.size();i++){
		if(n[i]!=' '){
			cnt++;
		}
	}
	cout<<cnt;
	return 0;
}
