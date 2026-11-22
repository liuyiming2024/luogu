
#include<bits/stdc++.h>
using namespace std;
int main(){
	int a,b,c,d;
	cin>>a>>b>>c>>d;
	int x,y;
	if(d>=b){ y=d-b; }
	else{ d+=60; y=d-b; c--; }
	x=c-a;
	cout<<x<<" "<<y;
	return 0;
}
