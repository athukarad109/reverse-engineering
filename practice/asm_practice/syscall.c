#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>

int main(){
	write(1, "hello", 5);
	exit(11);
	return 0;
}
