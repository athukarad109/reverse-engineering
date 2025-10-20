#include "connect4.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static game_state_t *g_state = NULL;
const char *move_descs_local[7] = {
	"Drop in far left","Drop in column 2","Drop in column 3",
	"Drop in middle","Drop in column 5","Drop in column 6","Drop in far right"
};
const char *move_descs[] = {
	"Drop in far left bro",
	"Drop in column 2",
	"Drop in column 3",
	"Drop in column 4",
	"Drop in column 5",
	"Drop in column 6",
	"Drop in far right bro"
};

void *game_init(void) {
	g_state = malloc(sizeof(game_state_t));
	if (!g_state) return NULL;
	g_state->current = 'X';
	g_state->cols = 3;
	g_state->rows = 3;
	memset(g_state->board, ' ', sizeof(g_state->board));
	fprintf(stderr, "dummy: game_init -> %p\n", (void*)g_state);
	return g_state;
}

int game_play(void *state, int column) {
	fprintf(stderr, "dummy: game_play(state=%p, column=%d)\n", state, column);
	/* pretend move valid if 0 <= column < cols and top is space */
	game_state_t *s = state;
	if (column < 0 || column >= (int)s->cols) return -1;
	if (s->board[column] != ' ') return -1;
	s->board[(s->rows - 1) * s->cols + column] = (char)s->current;
	/* toggle */
	if (s->current == 'X') s->current = 'O'; else s->current = 'X';
	return 0;
}

int check_winner(void *state) {
	/* trivial: always return 0 for dummy */
	return 0;
}

void game_enumerate_plays(void *state, move_callback_t cb, void *userdata) {
	game_state_t *s = state;
	for (int i = 0; i < (int)s->cols; ++i) {
		if (s->board[i] == ' ') cb(i, move_descs[i], userdata);
	}
}
