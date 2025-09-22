
int callee(int a, int b) {
  return a + b;
}

int caller() {
  return callee(0xf00d, 0xbeef);
}
