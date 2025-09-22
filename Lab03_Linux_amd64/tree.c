#define NULL 0

struct btNode {
  struct btNode* left;
  struct btNode* right;
  char val;
};

struct btNode tnode1, tnode2, tnode3;

struct btNode tnode1 = { &tnode2, &tnode3, 'B' };
struct btNode tnode2 = { NULL,    NULL,    'A' };
struct btNode tnode3 = { NULL,    NULL,    'C' };

struct btNode* troot = &tnode1;
