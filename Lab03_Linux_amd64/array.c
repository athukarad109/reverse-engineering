
int demo_array(int* ptrParamArray) {
  static int index;
  static int staticArray[] = { 1, 2, 4, 8, 16, 32, 0x1234 };

  static int static_const;
  static int static_var;
  static int ptr_const;
  static int ptr_var;

  static_const = staticArray[2];
  static_var = staticArray[index];
  ptr_const = ptrParamArray[3];
  ptr_var = ptrParamArray[index];
}
