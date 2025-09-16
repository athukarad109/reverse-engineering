.global add_two
add_two:
	movl %edi, %eax
	addl %esi, %eax
	ret
