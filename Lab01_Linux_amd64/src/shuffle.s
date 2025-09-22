.intel_syntax noprefix
.global shuffle
.extern rand

.text
shuffle:
    push rbp
    mov rbp, rsp
    push rbx
    push r12
    push r13
    push r14
    push r15

    mov r12, rdi      
    mov r13d, 51       

shuffle_loop:
    cmp r13, 0        
    jl end_shuffle    

    sub rsp, 8        
    call rand
    add rsp, 8

    mov r14, rax      
    mov r15d, r13d     
    inc r15d
    
    xor rdx, rdx
    mov rax, r14
    idiv r15
    
    mov r14d, edx      

    mov ecx, [r12 + r13 * 4]
    mov edx, [r12 + r14 * 4]

    mov [r12 + r14 * 4], ecx
    mov [r12 + r13 * 4], edx

    dec r13           
    jmp shuffle_loop

end_shuffle:
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    pop rbp
    ret