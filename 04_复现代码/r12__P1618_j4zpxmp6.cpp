#include<bits/stdc++.h>
using namespace std;
int a,b,c;
bool check1(int n) {
    string a = to_string(n);
    if (a.size() != 3) return 0;
    for (int i = 0; i < a.size(); i++)
        for (int j = 0; j < a.size(); j++) {
            if (i != j)
                if (a[i] == a[j])
                    return 0;
            if (a[i] == '0' || a[j] == '0')
                return 0;
        }
    return 1;
}
bool check2(int n, int m) {
    string a = to_string(n), b = to_string(m);
    for (int i = 0; i < a.size(); i++)
        for (int j = 0; j < b.size(); j++)
            if (a[i] == b[j]) return 0;
    return 1;
}
int main(){
    int cnt = 0;
    cin >> a >> b >> c;
    if (a == 0 || b == 0 || c == 0) { cout << "No!!!"; return 0; }
    for (int i = 1; i <= 9; i++) {
        for (int j = 1; j <= 9; j++) {
            if (i == j) continue;
            for (int k = 1; k <= 9; k++) {
                if (i == k || j == k) continue;
                int num1 = i * 100 + j * 10 + k;
                if (num1 % a) continue;
                int num2 = num1 / a * b;
                if (num2 % b || !check1(num2) || !check2(num1, num2)) continue;
                int num3 = num2 / b * c;
                if (num3 % c || !check1(num3) || !check2(num1, num3) || !check2(num2, num3)) continue;
                cnt++;
                cout << num1 << " " << num2 << " " << num3 << "\n";
            }
        }
    }
    if (cnt == 0) cout << "No!!!";
    return 0;
}
