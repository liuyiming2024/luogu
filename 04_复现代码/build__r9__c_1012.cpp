
#include <iostream>
#include <algorithm>
using namespace std;
bool cmp(string a, string b){ return a + b > b + a; }
int main(){
 int n; string a[21]; cin >> n;
 for (int i = 1; i <= n; i++) cin >> a[i];
 sort(a + 1, a + n + 1, cmp);
 for (int i = 1; i <= n; i++) cout << a[i];
 return 0;
}
