global _start

section .text

_start:
    ; write "Hello, World!" to stdout
    mov rax, 1
    mov rdi, 1
    mov rsi, hello
    mov rdx, 11
    syscall 

    mov rax, 60
    mov rdi, 123
    syscall

section .data:
    hello: db 'Hello world'