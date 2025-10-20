#ifndef CONNECT4_H
#define CONNECT4_H

#ifdef __cplusplus
extern "C"{
#endif

#include <stdint.h>

// Game state layout	
typedef struct{
	uint32_t current;
	uint32_t cols;
	uint32_t rows;
	char board[42];
}game_state_t;

//callback used by game_enumerate_plays

typedef void (*move_callback_t)(int moveIndex, const char *description, void *userdata);

// API exported

void *game_init(void);
int game_play(void *state, int column);
int check_winner(void *state);
void game_enumerate_plays(void *state, move_callback_t cb, void *userdata);

extern const char *move_descs[];

#ifdef __cplusplus
}
#endif

#endif



