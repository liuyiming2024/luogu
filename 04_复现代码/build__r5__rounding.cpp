#include <cstdio>
#include <iomanip>
#include <iostream>
int main(){
 printf("printf .125 -> %.2f\n", 549.125);
 printf("printf .625 -> %.2f\n", 353.625);
 printf("printf .135 -> %.2f\n", 549.135);
 printf("printf .375 -> %.2f\n", 549.375);
 std::cout << "cout .125 -> " << std::fixed << std::setprecision(2) << 549.125 << "\n";
 std::cout << "cout .625 -> " << std::fixed << std::setprecision(2) << 353.625 << "\n";
 return 0;
}
