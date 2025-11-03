global _start

section .text
_start:
    mov rax, 1
    mov rdi, 1
    mov rsi, inputtext
    mov rdx, inplength
    syscall

user_input:
    mov rax, 0
    mov rdi, 0
    mov rsi, name
    mov rdx, 100
    syscall

print_hello:
    mov rax, 1
    mov rdi, 1
    mov rsi, hello
    mov rdx, hello_len
    syscall
    mov rbx, rax ;users length is stored in rax after input is completed, and moving it to rbx because we need rax

print_input:
    mov rax, 1
    mov rdi, 1
    mov rsi, name
    mov rdx, rbx 
    syscall

exit:
    mov rax, 60
    mov rdi, 12
    syscall

section .data
    inputtext : db "Enter name : "
    inplength : equ $-inputtext
    hello: db "Hello, "
    hello_len: equ $-hello

section .bss
    name: resb 100
