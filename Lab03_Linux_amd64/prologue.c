
int c;

int demo_func(int a, int b) {
#ifdef __GNUC__
  __asm volatile (".body_starts:\n");
#endif
#ifdef _M_IX86
  __asm {body_starts:}
#endif
  c = a + b;
#ifdef __GNUC__
  __asm volatile (".body_ends:\n");
#endif
#ifdef _M_IX86
  __asm {body_ends:}
#endif
}
