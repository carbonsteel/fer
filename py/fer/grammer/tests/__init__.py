from fer.ferutil import load_tests_simple
from . import test_parser

test_cases = (
  test_parser.TestParseCoord,
  test_parser.TestConsumeString,
)

def load_tests(loader, tests, pattern):
  return load_tests_simple(test_cases, loader, tests, pattern)