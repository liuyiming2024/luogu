
#include<bits/stdc++.h>
using namespace std;
int main(){
 string s1, s2; int cnt1 = 1, cnt2 = 1;
 cin >> s1 >> s2;
 for (size_t i = 0; i < s1.size(); i++) cnt1 *= s1[i] - 'A' + 1;
 for (size_t i = 0; i < s2.size(); i++) cnt2 *= s2[i] - 'A' + 1;
 if (cnt1 % 47 == cnt2 % 47) cout << "GO";
 else cout << "STAY";
 return 0;
}
