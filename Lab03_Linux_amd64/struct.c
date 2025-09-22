struct MyStruct {
  int a;
  char b;
  char c;
  short d;
};

int demo_struct(struct MyStruct* ptrParamStruct) {
  static struct MyStruct staticStruct = {1024, 2, 3, 4};

  static int static_field;
  static int ptr_field;
  
  static_field = staticStruct.c;
  ptr_field = ptrParamStruct->d;
}
