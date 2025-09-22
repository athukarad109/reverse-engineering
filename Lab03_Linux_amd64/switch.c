int demo_switch(int c) {
  switch (c) {
    case 0: return 0xdead;
    case 1: return 0xbeef;
    case 2: return 0xcafe;
    case 3: return 0xbabe;
    default: return 0;
  }
}
