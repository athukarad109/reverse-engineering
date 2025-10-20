#include <stdio.h>

int add();

int main(){
	printf("Hello World!\n");
	printf("Calling add function with 10, 4\n");
	printf("Addition : %d", add(10, 4));
}

int add(int a, int b){
	return a+b;
}
