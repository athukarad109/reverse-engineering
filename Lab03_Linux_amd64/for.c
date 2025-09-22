int before_for() {}
int init_for() {}
int test_for() {}
int inside_for() {}
int step_for() {}
int after_for() {}

int demo_for() {
  before_for();
  for (init_for(); test_for(); step_for()) {
    inside_for();
  }
  after_for();
}
