default:all

labcrackme: keygen.c
	gcc -O3 -o $@ $< -lcrypto
	strip $@

dbg_labcrackme: keygen.c
	gcc -D_DEBUG -O1 -g -o $@ $< -lcrypto

all: labcrackme dbg_labcrackme