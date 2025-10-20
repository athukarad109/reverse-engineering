#include "connect4.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>


// functions to implement

/*
static game_state_t *g_state = NULL;
const char *move_descs[] = {};
void *game_init(void) {};
int game_play(void *state, int column) {};
int check_winner(void *state) {};
void game_enumerate_plays(void *state, move_callback_t cb, void *userdata) {};

*/

const char *move_descs[] = {
    "1. Place at top-left",
    "2. Place at top-middle",
    "3. Place at top-right",
    "4. Place at middle-left",
    "5. Place at center",
    "6. Place at middle-right",
    "7. Place at bottom-left",
    "8. Place at bottom-middle",
    "9. Place at bottom-right"
};

static game_state_t *g_state = NULL;

void *game_init(void){
    g_state = malloc(sizeof(game_state_t));
    if (!g_state){
        return NULL;
    }

    g_state -> current = 'X';
    g_state -> cols = 3;
    g_state -> rows = 3;
    memset(g_state -> board, ' ', sizeof(g_state -> board));

    return g_state;
}

int check_winner(void *state){
    game_state_t *s = (game_state_t *)state;
    char *b = s -> board;

    // Horizontal check
    for (int r = 0; r < s->rows; r++){
        int idx = r * s -> cols;
        if(b[idx] != ' ' && b[idx] == b[idx + 1] && b[idx + 1] == b[idx + 2]){
            return b[idx];
        }
    }

    //Vertical check
    for (int c = 0; c < s->cols; c++){
        if(b[c] != ' ' && b[c] == b[c+3] && b[c+3] == b[c+6]){
            return b[c];
        }
    }

    //Diagonal
    if (b[0] != ' ' && b[0] == b[4] && b[4] == b[8]){
        return b[0];
    }
    if (b[2] != ' ' && b[2] == b[4] && b[4] == b[8]){
        return b[2];
    }

    //If empty spaces game continues
    for (int i = 0; i < s->cols * s->rows; i++){
        if(b[i] == ' '){
            return 0;
        }
    }

    //If draw return -2
    return -2;

}

int game_play(void *state, int moveIndex){
    game_state_t *s = (game_state_t *)state;
    char *b = s -> board;

    // Checking if input index is greater
    if (moveIndex < 0 || moveIndex >= s -> cols * s -> rows){
        return -1;
    }

    // Checking if input index is already filled
    if (b[moveIndex] != ' '){
        return -1;
    }

    b[moveIndex] = (char)s -> current;

    int winner = check_winner(state);

    if(winner == 0){
        if (s -> current == 'X'){
            s -> current = 'O';
        }
        else{
            s -> current = 'X';
        }
        return 0;
    }

    return winner;

}

void game_enumerate_plays(void *state, move_callback_t cb, void *userdata){
    game_state_t *s = (game_state_t *)state;
    for (int i = 0; i < s -> cols * s -> rows; i++){
        if(s -> board[i] == ' '){
            cb(i, move_descs[i], userdata);
        }
    }
}




