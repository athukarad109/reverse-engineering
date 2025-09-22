int globalVar = 6;

int demo_vars(int paramVar) {
  int localVar = 8;
  paramVar--;

  globalVar = 9;
  static int staticVar = 7;
  staticVar++;
}

int main() {
  demo_vars(10);
}
