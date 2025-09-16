#include <stdio.h>
#include <stdlib.h>
#include <time.h>

typedef int boolean;
#define FALSE 0
#define TRUE 1

typedef int DECK[52];
#define lenof(arr) (sizeof(arr)/sizeof(arr[0]))

#ifdef _WIN32
#ifndef _WIN64
#define CDECL _cdecl
#else
#define CDECL
#endif
#else
#define CDECL
#endif

/**
 * Shuffle the complete deck
 *
 * This function rearranges the cards of the deck, selecting from all possible
 * permutations uniformly. Stated differently, the first card must be chosen
 * from all 52 cards with equal chance. The second card must be chosen from the
 * remaining 51 cards with equal chance, and so on, until cards for each of the
 * 52 positions have been chosen. No card may appear twice.
 *
 * This function must be implemented using an external assembly file. On
 * Windows platforms, this is likely the Microsoft Macro Assembler (MASM). On
 * Linux, this is the GNU assembler, which can be invoked via GCC. On macOS,
 * this is likely the LLVM assembler, which can be invoked via Clang.
 *
 * @param deck the initialized 52-card deck to shuffle
 */
void CDECL shuffle(DECK deck);

/**
 * Compare two hands, and identify the winning hand
 *
 * The function scores the two given hands and returns a value indicating the
 * winning hand. From highest to lowest, poker hands are scored as follows:
 *
 *  # Straight Flush: Five cards of consecutive rank of the same suit. If the
 *    high card is an Ace, this is called a "Royal Flush."
 *  # Four of a Kind: Four cards of equal rank.
 *  # Full House: Three of a Kind and a distinct Pair.
 *  # Flush: Five cards of the same suit.
 *  # Straight: Five cards of consecutive rank.
 *  # Three of a Kind: Three cards of equal rank.
 *  # Two Pair: Two distinct Pairs.
 *  # Pair: Two cards of equal rank.
 *
 * Note: an Ace may be played low (as if 1) or high (one greater than King),
 * but cannot be played as both simultaneously. When played low, it is also
 * scored low. For example, A-2-3-4-5 loses to 2-3-4-5-6. Even though the first
 * hand has an Ace, which is normally of the highest rank, it has been played
 * low to form the straight, causing it to have the lowest rank.
 *
 * Ties are broken by the rank of cards that score the hand. In the case of a
 * Full House, the rank of the Three of a Kind is considered first. If it is
 * still a tie, the rank of the Pair is considered next. If it is still a tie,
 * non-scoring cards are considered from highest to lowest. The same principle
 * follows for the other kinds of hands.
 *
 * This poker game implements a "House Rule" to break ties using the suits of
 * scoring cards. This only applies when, after comparison of all the ranks,
 * there is still a tie. The suits are scored highest to lowest: Spades,
 * Hearts, Diamonds, Clubs. The order in which cards are compared by suit is
 * the same as they were ordered when compared by rank. With this house rule,
 * it is impossible to remain tied, because every card is unique.
 *
 * @param hand0 a pointer to the first hand
 * @param hand1 a pointer to the second hand
 * @return 0 if the first hand wins or 1 if the second hand wins
 */
int compare_hands(int* hand0, int* hand1);
