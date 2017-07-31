from unittest import TestSuite

def load_tests_simple(test_cases, loader, tests, pattern):
  suite = TestSuite()
  for test_class in test_cases:
    tests = loader.loadTestsFromTestCase(test_class)
    suite.addTests(tests)
  return suite