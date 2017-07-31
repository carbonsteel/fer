import io
import unittest

from .. import parser, common

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
      self.assertEqual(result.error, "expected bytestring {}".format(repr(string)))
      self.assertEqual(result.causes[0].error, "unexpected bytes {}".format(repr(string2)))
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
      self.assertEqual(result.error, "expected bytestring {}".format(repr(string)))
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