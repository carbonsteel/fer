#!/usr/bin/python2
NULLPTR = 0

D_Main =            0x0
D_Natural =         0x1
S_Natural =             0x1
D_Natural_One =       0x0
D_Natural_Next =      0x1

D_NaturalMath =     0x2
S_NaturalMath =         0x0
D_NaturalMath_sum =   0x0

class magicpu(object):
  def __init__(self):
    self._stack = []
    self._stack_maxsize = 32
  def trace(self):
    print("Stack:")
    print(format(self._stack))
    print("Stack pointer:")
    print(format(self.stack_pointer()))
  def stack_pointer(self):
    return len(self._stack)-1
  def stack_read(self, sp):
    return self._stack[sp]
  def stack_push(self, v):
    if self._stack_maxsize == len(self._stack):
      raise ValueError("Stackoverflow!")
    self._stack.append(v)
  def stack_pop(self):
    return self._stack.pop()

def trace(msg):
  print(msg)

def T_NaturalMath_sum(cpu, pv_a, pv_b):
  locals = {
    "done": False,
  }
  while (not locals["done"]):
    v_a = cpu.stack_read(pv_a)
    trace(pv_a)
    trace(v_a)
    v_b = cpu.stack_read(pv_b)
    trace(pv_b)
    trace(v_b)
    [lambda: trace("a is One, b is One")
          or cpu.stack_push(D_Natural_Next)
          or cpu.stack_push(pv_b)
          or locals.update({"done":True}),
      lambda: trace("a is One, b is Next")
          or cpu.stack_push(D_Natural_Next)
          or cpu.stack_push(pv_b)
          or locals.update({"done":True}),
      lambda: trace("a is Next, b is One")
          or cpu.stack_push(D_Natural_Next)
          or cpu.stack_push(pv_a)
          or locals.update({"done":True}),
      lambda: trace("a is Next, b is Next")
          or cpu.stack_push(D_Natural_Next)
          or cpu.stack_push(cpu.stack_pointer()+2)
          or cpu.stack_push(D_Natural_Next)
          or cpu.stack_push(cpu.stack_pointer()+2)
    ][ v_a
    + (v_b << S_Natural)]()

def main(cpu):
  cpu.stack_push(D_Natural_Next)
  cpu.stack_push(cpu.stack_pointer()+2)
  cpu.stack_push(D_Natural_One)
  T_NaturalMath_sum(cpu, cpu.stack_pointer(), cpu.stack_pointer())

if __name__ == "__main__":
  _cpu = magicpu()
  try:
    main(_cpu)
  finally:
    _cpu.trace()