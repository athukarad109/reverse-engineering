#include <stdio.h>
#include "mathutils.h"

extern int add_two(int,  int);

int main(){
	printf( "Hello world!\n");
	printf("Added with C file : %d\n", add(4, 5));
	printf("Added with asm file: %d\n", add_two(4, 5));
	return 0;
}
