#define NULL 0

struct llNode {
  struct llNode* prev;
  struct llNode* next;
  char val;
};

struct llNode lnode1, lnode2, lnode3;

struct llNode lnode1 = { NULL,    &lnode2, 'A' };
struct llNode lnode2 = { &lnode1, &lnode3, 'B' };
struct llNode lnode3 = { &lnode2, NULL,    'C' };

struct llNode* lhead = &lnode1;
