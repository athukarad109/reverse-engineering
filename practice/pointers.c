#include <stdio.h>

int main(){
    int n = 1;
    int *pN = &n;
    printf("Address of age : %p\n", &n);
    printf("Actual n: %d\n", n);
    printf("Value of pN : %p\n", pN);

    printf("Pointer : %d", *pN);
    return 0;
}