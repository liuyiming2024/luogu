#include <iostream>
#include <cstdio>
#include <cstring>
using namespace std;
long long n,k;
int a[100000005];
int main()
{
    cin>>n;
    for(int i=1;i<=n;i++)
    {
        cin>>k;
        a[k]++;
        if(a[k]==2)
        {
            a[k]=0;
        }
    }
    for(int i=1;i<=10000000;i++)
    {
        if(a[i]==1)
        {
            cout<<i;
            break;
        }
    }
    return 0;
}
