int before_while() {}
int inside_while() {}
int after_while() {}

int demo_while(int c) {
  before_while();
  while (c != 0) {
    inside_while();
  }
  after_while();
}
