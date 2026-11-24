#include<iostream>
using namespace std;
int st[9], bok[9] = {0};
void dfs(int step) {
    if (step == 9) {
        int a = 100*st[0] + 10*st[1] + st[2];//第一个三位数
        int b = 100*st[3] + 10*st[4] + st[5];//第二个三位数
        int c = 100*st[6] + 10*st[7] + st[8];//第三个三位数
        //下面是判断三位数是否成1：2：3的比例
        if (3*a == c && 2*a == b) {
            cout << st[0] << st[1] << st[2] << ' '
                 << st[3] << st[4] << st[5] << ' '
                 << st[6] << st[7] << st[8] << '\n';
        }   
    }
    //下面是生成全排列
    for (int i = 1; i <= 9; i++) {
        if (bok[i]) continue;
        bok[i] = true;
        st[step] = i;
        dfs(step+1);
        bok[i] = false;
    }
}
int main(){
    dfs(0);
    return 0;
}