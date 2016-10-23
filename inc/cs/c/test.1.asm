section .text

  global T_NaturalMath_sum
T_NaturalMath_sum:
T_NaturalMath_sum_0:
  ; a and b are garenteed to be both of Natural
  ; is a one?
  cmp r14,D_Natural_One
  jne T_NaturalMath_sum_1
  ; a is one
  sub rsp,8
  mov [rsp+4],r13
  mov [rsp+8],D_Natural_Next
  mov rax,rsp+8
  jmp [rsp]
T_NaturalMath_sum_1:
  ; a is next
  ; is b one?
  cmp r13,D_Natural_One
  je T_NaturalMath_sum_2
  ; b is one
  sub rsp,8
  mov [rsp+4],r14
  mov [rsp+8],D_Natural_Next
  mov rax,rsp+8
  jmp T_Main_1
T_NaturalMath_sum_2:
  ; a is next and b is next
  inc r15
  sub rsp,16
T_NaturalMath_sum_2a:
  mov [rsp+4],
  mov [rsp+8],D_Natural_Next
  mov [rsp+12],rsp+4
  mov [rsp+16],D_Natural_Next
  mov rax,rsp+8
  jmp T_Main_1

  global  T_main
; dumb and unoptimized code for three.1.fer
T_Main:
T_Main_0:
  sub rsp, 24
  ; one
  mov [rbp-4],D_Natural_One
  ; a next
  mov [rbp-8],rbp-4
  mov [rbp-12],D_Natural_Next
  ; one
  mov [rbp-16],D_Natural_One
  ; b next
  mov [rbp-20],rbp-16
  mov [rbp-24],D_Natural_Next
  ; set params
  ; a and b could point to the same place
  mov r14,[rbp-12]
  mov r13,[rbp-24]
  call T_NaturalMath_sum
  
T_Main_1:
; sys_exit 0
  mov     rdi,rax
  mov     rax,60
  syscall



section .data

D_Main db             0x0
D_Natural db          0x1
D_Natural_One db      0x2
D_Natural_Next db     0x3
D_NaturalMath db      0x4
D_NaturalMath_sum db  0x5

