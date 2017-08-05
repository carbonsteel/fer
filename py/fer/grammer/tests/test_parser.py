import io
import unittest

from .. import parser, common


class TestParseCoord(unittest.TestCase):
  def test_less_than(self):
    a = parser.ParseCoord(file="file_a", line=1, column=1, level=1)
    b = parser.ParseCoord(file="file_b1", line=2, column=1, level=1)
    self.assertTrue(a < b)
    b = parser.ParseCoord(file="file_b2", line=1, column=2, level=1)
    self.assertTrue(a < b)
    b = parser.ParseCoord(file="file_b3", line=2, column=2, level=1)
    self.assertTrue(a < b)
    b = parser.ParseCoord(file="file_b4", line=1, column=1, level=2)
    self.assertTrue(a < b)

  def test_equal(self):
    a = parser.ParseCoord(file="file_a", line=1, column=1, level=1)
    b = parser.ParseCoord(file="file_b1", line=1, column=1, level=1)
    self.assertTrue(a == b)
    b = parser.ParseCoord(file="file_a", line=3, column=1, level=1)
    self.assertTrue(a != b)
    b = parser.ParseCoord(file="file_a", line=1, column=3, level=1)
    self.assertTrue(a != b)
    b = parser.ParseCoord(file="file_a", line=1, column=1, level=3)
    self.assertTrue(a != b)
    b = parser.ParseCoord(file="file_a", line=1, column=1, level=1)
    self.assertTrue(a == b)

  def test_diff(self):
    a = parser.ParseCoord(file="file_a", line=10, column=5, level=1)
    b = parser.ParseCoord(file="file_b1", line=3, column=1, level=1)
    self.assertTrue(a > b)
    self.assertEqual(a - b, parser.ParseCoordDistance(lines=7, columns=4, levels=0))
    self.assertTrue(parser.ParseCoordDistance.NIL < a - b)
    self.assertEqual(a - a, parser.ParseCoordDistance.NIL)


class TestConsumeString(unittest.TestCase):

  def test_string_predicate_equal(self):
    string = "my simple string"
    string_len = len(string)
    name = "nameless"
    sio = io.StringIO(string)
    reader = parser.ParseReader(sio, name)
    result = reader.consume_string(parser.StringPredicate(string), string_len, string_len)
    try:
      self.assertEqual(result.value, string)
    except AttributeError:
      raise AssertionError('Result must be a ParseValue')

  def test_string_predicate_not_equal(self):
    string = "my simple string"
    string2 = "my simpel string"
    string_len = len(string)
    name = "nameless"
    sio = io.StringIO(string2)
    reader = parser.ParseReader(sio, name)
    result = reader.consume_string(parser.StringPredicate(string), string_len, string_len)
    try:
      self.assertEqual(result.error, "expected string {}".format(repr(string)))
      self.assertEqual(result.causes[0].error, "unexpected terminal {}".format(repr(string2)))
    except AttributeError:
      raise AssertionError('Result must be a ParseError')

  def test_string_predicate_early_eof(self):
    string = "my simple string"
    string2 = "my string"
    string_len = len(string)
    name = "nameless"
    sio = io.StringIO(string2)
    reader = parser.ParseReader(sio, name)
    result = reader.consume_string(parser.StringPredicate(string), string_len, string_len)
    try:
      print(common.civilize_parse_error(result))
      self.assertEqual(result.error, "expected string {}".format(repr(string)))
      self.assertEqual(result.causes[0].error, 'unexpected eof after {}'.format(repr(string2)))
    except AttributeError:
      raise AssertionError('Result must be a ParseError')

  def test_fixed_escaped_predicate_equal(self):
    string = "my simple\\' string"
    string_len = len(string)
    print(string_len)
    name = "nameless"
    sio = io.StringIO(string + "  ") # added buffer before eof, otherwise peeking wont work.
    reader = parser.ParseReader(sio, name)
    result = reader.consume_string(parser.FixedEscapedClassPredicate.factory("^'", "\\\\"), string_len, string_len)
    try:
      self.assertEqual(result.value, string.replace('\\', ''))
    except AttributeError:
      print(common.civilize_parse_error(result))
      raise AssertionError('Result must be a ParseValue')