from fer.ferutil import load_tests_simple
from . import test_varcheck

test_cases = (
  test_varcheck.Tests,
)

def load_tests(loader, tests, pattern):
  return load_tests_simple(test_cases, loader, tests, pattern)