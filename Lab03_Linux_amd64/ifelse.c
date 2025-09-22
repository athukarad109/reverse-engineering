int before_ifelse() {}
int inside_ifpart() {}
int inside_elsepart() {}
int after_ifelse() {}

int demo_ifelse(int c) {
  before_ifelse();
  if (c) {
    inside_ifpart();
  } else {
    inside_elsepart();
  }
  after_ifelse();
}
