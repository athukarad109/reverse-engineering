#include <stdio.h>
#include <unistd.h>

int main(){
    printf("SC_PAGE_SIZE: 0x%x\n", _SC_PAGESIZE);
    printf("sysconf(_SC_PAGESIZE): 0x%lx\n", sysconf(_SC_PAGESIZE));
}