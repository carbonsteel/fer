section .text

  global  _start

_start:
; sys_write stdout msg len
  mov     rdi,1
  mov     rsi,msg
  mov     rdx,len
  mov     rax,1
  syscall

; sys_exit 0
  mov     rdi,0
  mov     rax,60
  syscall

section .data

; Hello, world!\n
msg db    "Hello, world!",0xa
; length of msg
len equ   $ - msg