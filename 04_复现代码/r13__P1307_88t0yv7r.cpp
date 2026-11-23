#include <iostream>
#include <algorithm>
using namespace std;
int main()
{
int n ;
cin >> n ;
int m = 0 ;
if ( n < 0 )
{
cout << "-" ;
n *= -1 ;
}
while ( n != 0 )
{
m = n % 10 + m * 10 ;
n /= 10 ;
}
cout << m << endl ;
return 0;
}
