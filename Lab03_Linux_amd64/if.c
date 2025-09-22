int before_if() {}
int inside_if() {}
int after_if() {}

int demo_if(int c) {
  before_if();
  if (c) {
    inside_if();
  }
  after_if();
}
