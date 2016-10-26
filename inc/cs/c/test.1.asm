section .text

  global T_NaturalMath_sum
T_NaturalMath_sum:
  ; a and b are garenteed to be both of Natural
  ; r14 points to a
  ; r13 points to b
  mov r8,[r14]
  mov r9,[r13]
  jmp [J_NaturalMath_sum+r8*2+r9]
J_NaturalMath_sum:
  dd T_NaturalMath_sum_0
  dd T_NaturalMath_sum_0
  dd T_NaturalMath_sum_1
  dd T_NaturalMath_sum_2
T_NaturalMath_sum_0:
  ; a is one
  ; b is one or next
  push r13
  push D_Natural_Next
  mov rax,rsp
  ret
T_NaturalMath_sum_1:
  ; a is next
  ; b is one
  push r14
  push D_Natural_Next
  mov rax,rsp
  ret
T_NaturalMath_sum_2:
  ; a is next
  ; b is next
  push ; RENDU ICI
  call T_NaturalMath_sum
  push 0
  push D_Natural_Next
  push rsp
  push D_Natural_Next

  ret

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
D_Natural_One db        0x0
D_Natural_Next db       0x1
D_NaturalMath db      0x2
D_NaturalMath_sum db    0x0