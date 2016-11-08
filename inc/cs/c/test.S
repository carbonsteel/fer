
# borkne code for three.1.fer

# as test.S -o test.o -g && ld test.o -o test

.text
.global T_NaturalMath_sum
T_NaturalMath_sum:
  # a and b are garenteed to be both of Natural#
  # r14 points to a
  # r13 points to b
  movq (%r14), %r8
  movq (%r13), %r9
  lea T_NaturalMath_sum_2, %rax
  lea J_NaturalMath_sum, %rbx
  lea J_NaturalMath_sum_test, %rcx
  lea (%r9,%r8,2), %r10
  lea J_NaturalMath_sum(,%r10,4), %r11
  mov (%r11), %edx
  jmpq *%rdx
J_NaturalMath_sum:
  .int T_NaturalMath_sum_0
  .int T_NaturalMath_sum_0
  .int T_NaturalMath_sum_1
J_NaturalMath_sum_test:
  .int T_NaturalMath_sum_2
T_NaturalMath_sum_0:
  # a is one
  # b is one or next
  pushq %r13
  pushq D_Natural_Next
  mov %rsp, %rax
  ret
T_NaturalMath_sum_1:
  # a is next
  # b is one
  pushq %r14
  pushq D_Natural_Next
  mov %rsp, %rax
  ret
T_NaturalMath_sum_2:
  # a is next
  # b is next
  movq 8(%r14), %r14
  movq 8(%r13), %r13
  call T_NaturalMath_sum
  pushq %rax
  pushq D_Natural_Next
  pushq %rsp
  pushq D_Natural_Next
  ret

.global _start
.global  T_main
_start:
T_Main:
T_Main_0:
  # one
  pushq D_Natural_One
  # a next
  pushq %rsp
  pushq D_Natural_Next
  mov %rsp, %r14
  # one
  pushq D_Natural_One
  # b next
  pushq %rsp
  pushq D_Natural_Next
  # set params
  # a and b could point to the same place
  mov %rsp, %r13
  call T_NaturalMath_sum
  # sys_exit 0
  mov %rax, %rdi
  mov $60, %rax
  syscall



.data

D_Main:
.quad               0x0
D_Natural:
.quad               0x1
D_Natural_One:
.quad                 0x0
D_Natural_Next:
.quad                 0x1
D_NaturalMath:
.quad               0x2
D_NaturalMath_sum:
.quad                 0x0




.end # END
