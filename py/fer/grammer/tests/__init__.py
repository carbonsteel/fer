from unittest import TestSuite
from . import parser

test_cases = (
  parser.TestConsumeString,
)

def load_tests(loader, tests, pattern):
  suite = TestSuite()
  for test_class in test_cases:
    tests = loader.loadTestsFromTestCase(test_class)
    suite.addTests(tests)
  return suite