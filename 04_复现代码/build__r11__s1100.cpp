
#include<bits/stdc++.h>
using namespace std;
long long n;
string zhuan(long long ans)
{
	string a="";
	while(ans)
	{
		a=char(ans%2+48)+a;
		ans/=2;
	}
	for(int i=1;a.size()<32;i++)
	{
		a='0'+a;
	}
	return a;
}
string huan(string a)
{
	string b="";
	for(int i=16;i<32;i++) b+=a[i];
	for(int i=0;i<16;i++) b+=a[i];
	return b;
}
long long jieguo(string a)
{
	long long k=1,sum=0;
	for(int i=a.size()-1;i>=0;i--)
	{
		sum+=(int(a[i])-48)*k;
		k*=2;
	}
	return sum;
}
int main()
{
	cin>>n;
	cout<<jieguo(huan(zhuan(n)));
	return 0;
}
