
#include <iostream>
using namespace std;
int main(){
    int n, k; scanf("%d %d",&n,&k);
    int count = 0;
    int end = 0;
    do {
        count += n;
        end += n;
        n = end / k;
        end %= k;
    } while (n > 0);
    printf("%d\n",count);
    return 0;
}
