#include "poker.h"

#define HIST_SIZE 14   // 1..13 for ranks

typedef int HIST[HIST_SIZE];

// Build histogram of ranks
void compute_hist(int* hand, HIST hist) {
    for (int i = 0; i < HIST_SIZE; i++) hist[i] = 0;
    for (int i = 0; i < 5; i++) {
        int rank = hand[i] & 0x0f;
        hist[rank]++;
    }
}

// Check for single pair
int check_pair(HIST hist, int from) {
    for (int i = from; i < HIST_SIZE; i++) {
        if (hist[i] == 2) {
            return i;
        }
    }
    return 0;
}

// Check for three of a kind
int check_3ofkind(HIST hist) {
    for (int i = 1; i < HIST_SIZE; i++) {
        if (hist[i] == 3) {
            return i;
        }
    }
    return 0;
}

// Check for four of a kind
int check_4ofkind(HIST hist) {
    for (int i = 1; i < HIST_SIZE; i++) {
        if (hist[i] == 4) {
            return i;
        }
    }
    return 0;
}

// Two pair check
int check_2pair(HIST hist) {
    int first_pair = check_pair(hist, 1);
    if (first_pair == 0 || first_pair == HIST_SIZE - 1) {
        return 0;
    }
    int second_pair = check_pair(hist, first_pair + 1);
    if (second_pair == 0) {
        return 0;
    }
    return (second_pair << 4) | first_pair; // pack both ranks
}

// Full house check
int check_fullhouse(HIST hist) {
    int tok = check_3ofkind(hist);
    int pair = check_pair(hist, 1);
    if (tok && pair) {
        return (tok << 4) | pair;
    }
    return 0;
}

// Straight check
int check_straight(HIST hist) {
    for (int i = 1; i <= 9; i++) {  // 1..9 possible starts
        int run = 0;
        for (int j = i; j < i + 5; j++) {
            if (hist[j] > 0) run++;
            else break;
        }
        if (run == 5) return i + 4; // high card of straight
    }
    // Special case: A-2-3-4-5
    if (hist[1] && hist[2] && hist[3] && hist[4] && hist[13]) {
        return 5;
    }
    return 0;
}

// Flush check (all same suit)
int check_flush(int* hand) {
    int suit = (hand[0] >> 4) & 0x0f;
    for (int i = 1; i < 5; i++) {
        if (((hand[i] >> 4) & 0x0f) != suit) return 0;
    }
    return suit + 1; // nonzero if flush
}

int compare_hands(int* hand0, int* hand1) {
    HIST h0, h1;
    compute_hist(hand0, h0);
    compute_hist(hand1, h1);

    // Evaluate hands
    int flush0 = check_flush(hand0);
    int flush1 = check_flush(hand1);
    int straight0 = check_straight(h0);
    int straight1 = check_straight(h1);
    int four0 = check_4ofkind(h0);
    int four1 = check_4ofkind(h1);
    int fh0 = check_fullhouse(h0);
    int fh1 = check_fullhouse(h1);
    int tok0 = check_3ofkind(h0);
    int tok1 = check_3ofkind(h1);
    int two0 = check_2pair(h0);
    int two1 = check_2pair(h1);
    int pair0 = check_pair(h0, 1);
    int pair1 = check_pair(h1, 1);

    // Straight flush
    if (straight0 && flush0 && !(straight1 && flush1)) return 0;
    if (straight1 && flush1 && !(straight0 && flush0)) return 1;

    // Four of a kind
    if (four0 && !four1) return 0;
    if (four1 && !four0) return 1;

    // Full house
    if (fh0 && !fh1) return 0;
    if (fh1 && !fh0) return 1;

    // Flush
    if (flush0 && !flush1) return 0;
    if (flush1 && !flush0) return 1;

    // Straight
    if (straight0 && !straight1) return 0;
    if (straight1 && !straight0) return 1;

    // Three of a kind
    if (tok0 && !tok1) return 0;
    if (tok1 && !tok0) return 1;

    // Two pair
    if (two0 && !two1) return 0;
    if (two1 && !two0) return 1;

    // One pair
    if (pair0 && !pair1) return 0;
    if (pair1 && !pair0) return 1;

    // High card fallback: compare top ranks manually
    for (int r = 13; r >= 1; r--) {
        if (h0[r] != h1[r]) {
            return (h0[r] > h1[r]) ? 0 : 1;
        }
    }

    // If still tied, apply suit tiebreak
    int high0 = hand0[0], high1 = hand1[0];
    int suit0 = (high0 >> 4) & 0xf;
    int suit1 = (high1 >> 4) & 0xf;
    return (suit0 > suit1) ? 0 : 1;
}
