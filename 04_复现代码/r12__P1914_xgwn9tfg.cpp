#include <stdio.h>
int main(){
char a[1001];
int n, i;
scanf("%d%s", &n, a);
for(i = 0; a[i] != '\0'; i++)
putchar((a[i]-'a'+n)%26+'a');
return 0;
}
