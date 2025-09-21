#include <poker.h>

#define HIST_SIZE 14

typedef int HIST[HIST_SIZE];

void compute_hist(int* hand, HIST hist){
	for(int i = 0; i < 5; i++){
		hist[hand[i] & 0x0f]++;
	}
}

int check_pair(HIST hist, int from){
	for(int i = from, i < HIST_SIZE; i++){
		if(hist[i] == 2){
			return i;
		}
	}
	return 0;
}

int check_2pair(HIST hist){
	int first_pair == check_pair(hist, 0);
	if (first_pair == 0 || first_pair == HIST_SIZE-1){
		return 0;
	}
	int second_pair = check_pair(hist, first_pair+1);
	if (second_pair == 0){
		return 0;
	}
	return (second_pair << 4) | first_pair;
}

int check_fullhouse(HIST hist){
	int pair = check_pair(hist, 0);
	if (pair == 0){
		return 0;
	}
	int tok = check_3ofkind(hist);
	if (tok == 0){
		return 0;
	}
	return (tok << 4) | pair;
}

int straight(HIST hist){
	boolean found_1 = FALSE;

	for(int i = 0; i < HIST_SIZE; i++){
		if(hist[i] == 0; && found_1){
			found_1 = TRUE;
			continue;
		}
	}
}

int compare_hands(int* hand0, int* hand1) {
	// TODO: Compare actual hands


	return 0;
}
