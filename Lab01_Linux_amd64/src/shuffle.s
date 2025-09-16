.intel_syntax noprefix

.global shuffle

.text
shuffle:
//Pointer to the deck should be in RDI
	INT3
	RET
