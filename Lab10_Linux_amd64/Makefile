default:all

labcrackme: LabCrackme_submission.c
	gcc -O3 -o $@ $< -lcrypto
	strip $@

dbg_labcrackme: LabCrackme_submission.c
	gcc -D_DEBUG -O1 -g -o $@ $< -lcrypto

all: labcrackme dbg_labcrackme