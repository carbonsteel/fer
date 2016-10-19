section .text

  global  _start

_start:

T_NaturalMath_sum:
; sys_exit 0
  mov     rdi,0
  mov     rax,60
  syscall

section .data

D_Main db             0x0
D_Natural db          0x1
D_Natural_One db      0x2
D_Natural_Next db     0x3
D_NaturalMath db      0x4
D_NaturalMath_sum db  0x5

