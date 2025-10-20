#include <stdio.h>

int main(void){
	size_t i;
	size_t x = 11;
	size_t y = 0;

	for(i = 0; i < 10; i++){
		printf("%lu\n", i);
	}

	while(x > 0){
		printf("%lu\n", x);
		x--;
	}

	do{
		printf("%lu\n", y);
		y++;
	}while(y < 12);

}
