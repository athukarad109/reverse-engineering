struct InnerStruct {
  int a;
  char b;
  char c;
  short d;
};

struct OuterStruct {
  int tag;
  struct InnerStruct inners[10];
};

int demo_combo(struct OuterStruct* ptrParamOuterStruct) {
  static int result;
  static int index;
  result = ptrParamOuterStruct->inners[index].c;
}
