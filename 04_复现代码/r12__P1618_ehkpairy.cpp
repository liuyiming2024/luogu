#include <cstdio>
#include <cstring>
int a, b, c;
void red(void);
bool finish(int i, int j, int k);
int main() {
    bool no = true;
    scanf("%d%d%d", &a, &b, &c);
    red();
    for (int i = 100 + a - 100 % a; i <= 999; i += a) {
        int j, k;
        if (i / a * c > 999) break;
        j = i / a * b; k = i / a * c;
        if (finish(i, j, k)) {
            printf("%d %d %d\n", i, j, k);
            no = false;
        }
    }
    if (no) printf("No!!!");
    return 0;
}
void red(void) {
    if (a == 1) return;
    for (int i = a; i > 1; --i) {
        while (!(a % i) && !(b % i) && !(c % i))
            a /= i, b /= i, c /= i;
        if (a == 1) return;
    }
}
bool finish (int i, int j, int k) {
    bool ret = true, used[10];
    memset(used, 0, sizeof(used));
    used[i % 10] = used[i / 100] = used[i / 10 % 10] = true;
    used[j % 10] = used[j / 100] = used[j / 10 % 10] = true;
    used[k % 10] = used[k / 100] = used[k / 10 % 10] = true;
    for (int i = 1; i < 10; ++i)
        if (!used[i]) { ret = false; break; }
    return ret;
}
