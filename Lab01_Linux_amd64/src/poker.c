#include "poker.h"

int roundnum = 1;

char buf[80];

int chips[2] = { 100, 100 };

int winner = -1; // 0 is human. 1 is computer

char clubs[] = "Clubs";
char diamonds[] = "Diamonds";
char hearts[] = "Hearts";
char spades[] = "Spades";

char* suit_strs[] = { clubs, diamonds, hearts, spades };

char ace[] = "Ace";
char v2[] = "2";
char v3[] = "3";
char v4[] = "4";
char v5[] = "5";
char v6[] = "6";
char v7[] = "7";
char v8[] = "8";
char v9[] = "9";
char v10[] = "10";
char jack[] = "Jack";
char queen[] = "Queen";
char king[] = "King";

char* rank_strs[] = { NULL, ace, v2, v3, v4, v5, v6, v7, v8, v9, v10, jack,
		queen, king };

typedef enum _ACTION {
	ACTION_NONE = 0, ACTION_PLAY, ACTION_FOLD
} ACTION;

/**
 * Encoding cards: 4 bits suit (0-3), 4 bits rank (1-13)
 * 0 - Clubs
 * 1 - Diamonds
 * 2 - Hearts
 * 3 - Spades
 *
 * Ace is 1, numbers are 2 - 10, 11-Jack, 12-Queen, 13-King
 */
void init_deck(DECK deck) {
	for (int suit = 0; suit < 4; suit++) {
		for (int rank = 1; rank <= 13; rank++) {
			deck[suit * 13 + rank - 1] = suit << 4 | rank;
		}
	}
}

void print_card(int card) {
	int rank = card & 0xf;
	int suit = (card >> 4) & 0xf;
	printf("%s of %s\n", rank_strs[rank], suit_strs[suit]);
}

ACTION read_action() {
	while (1) {
		printf("Play[p] or Fold[f]? ");
		fgets(buf, sizeof(buf), stdin);
		switch (buf[0]) {
		case 'p':
		case 'P':
			return ACTION_PLAY;
		case 'f':
		case 'F':
			return ACTION_FOLD;
		default:
			printf("Invalid input. ");
		}
	}
}

ACTION ai_action(int* hand, int bet) {
	// AI plays with 50% probability
	if (rand() % 2 == 0) {
		return ACTION_PLAY;
	}
	return ACTION_FOLD;
}

void play_round(int first) {
	printf("Chips: Human has %d. AI has %d.\n", chips[0], chips[1]);
	// Both players must ante
	if (chips[0] < 2) {
		winner = 1;
		printf("Human cannot ante up. Sorry, you lose!\n");
		return;
	} else if (chips[1] < 2) {
		winner = 0;
		printf("AI cannot ante up. Congratulations, you win!\n");
		return;
	}
	printf("Round %d. Ante is 2 chips for both players. [ANYKEY] to continue:", roundnum);
	fgets(buf, sizeof(buf), stdin);

	int pot = 4;
	chips[0] -= 2;
	chips[1] -= 2;

	// Shuffle and deal

	DECK deck;
	init_deck(deck);
	shuffle(deck);

	// Assign the hands by reference into deck
	int* hand0 = &deck[0];
	int* hand1 = &deck[5];

	printf("Human's hand:\n");
	for (int i = 0; i < 5; i++) {
		print_card(hand0[i]);
	}
	printf("Chips: Human has %d. AI has %d.\n", chips[0], chips[1]);
	if (first == 0) {
		printf("The pot is at %d. Human plays first. Bet? ", pot);
		ACTION h_action = read_action();
		if (h_action == ACTION_FOLD) {
			printf("Human folds. AI takes the pot: %d\n", pot);
			chips[1] += pot;
			return;
		}
		int bet = chips[0] >= 3 ? 3 : chips[0];
		printf("Human bets %d chips\n", bet);
		chips[0] -= bet;
		pot += bet;
		printf("Pot is now at %d. AI plays second.\n", pot);
		ACTION c_action = ai_action(hand1, bet);
		if (c_action == ACTION_FOLD) {
			printf("AI folds. Human takes the pot: %d\n", pot);
			chips[0] += pot;
			return;
		}
		bet = chips[1] >= bet ? bet : chips[1];
		printf("AI calls %d chips\n", bet);
		chips[1] -= bet;
		pot += bet;
		printf("Pot is now at %d\n", pot);
	} else {
		printf("The pot is at %d. AI plays first.\n", pot);
		ACTION c_action = ai_action(hand1, -1);
		if (c_action == ACTION_FOLD) {
			printf("AI folds. Human takes the pot: %d\n", pot);
			chips[0] += pot;
			return;
		}
		int bet = chips[1] >= 3 ? 3 : chips[1];
		printf("AI bets %d chips\n", bet);
		chips[1] -= bet;
		pot += bet;
		printf("Pot is now at %d. Human plays second. Call? ", pot);
		ACTION h_action = read_action();
		if (h_action == ACTION_FOLD) {
			printf("Human folds. AI takes the pot: %d\n", pot);
			chips[1] += pot;
			return;
		}
		bet = chips[0] >= bet ? bet : chips[0];
		printf("Human calls %d chips\n", bet);
		chips[0] -= bet;
		pot += bet;
		printf("Pot is now at %d\n", pot);
	}
	printf("AI's hand:\n");
	for (int i = 0; i < 5; i++) {
		print_card(hand1[i]);
	}
	int round_winner = compare_hands(hand0, hand1);
	if (round_winner == 0) {
		printf("Human has the better hand.\n");
	} else {
		printf("AI has the better hand.\n");
	}
	chips[round_winner] += pot;
}

int main(int argc, char** argv) {
	printf("Welcome to poker!\n");

	srand(time(NULL));
	int first_better = rand() % 2;
	while (winner == -1) {
		play_round(first_better);
		first_better = (first_better + 1) % 2;
		roundnum++;
	}
}

