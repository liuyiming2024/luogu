
#include<bits/stdc++.h>
using namespace std;
int main(){
    char str[300];
    int count = 0;
    scanf("%s", str);
    for(int i = 0; str[i] != '@'; i++){
        if(str[i] == '(') count++;
        else if(str[i] == ')') count--;
        if(count < 0) break;
    }
    printf(count == 0 ? "YES\n" : "NO\n");
    return 0;
}
