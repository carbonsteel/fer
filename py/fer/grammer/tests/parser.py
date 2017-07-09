import io
import unittest

from .. import parser
from fer.ferutil import env
env.vars.init()

class TestConsumeString(unittest.TestCase):

  def test_string_predicate_equal(self):
    string = "my simple string"
    string_len = len(string)
    name = "nameless"
    sio = io.StringIO(string)
    reader = parser.ParseReader(sio, name)
    result = reader.consume_string(parser.StringPredicate(string), string_len, string_len)
    self.assertEqual(result.parse_kind, 'value')
    self.assertEqual(result.value, string)

  def test_string_predicate_not_equal(self):
    string = "my simple string"
    string2 = "my simpel string"
    string_len = len(string)
    name = "nameless"
    sio = io.StringIO(string2)
    reader = parser.ParseReader(sio, name)
    result = reader.consume_string(parser.StringPredicate(string), string_len, string_len)
    self.assertEqual(result.parse_kind, 'error')
    self.assertEqual(result.error, "expected bytestring `my simple string'")
    self.assertEqual(result.causes[0].error, 'unexpected eof')

  def test_string_predicate_early_eof(self):
    string = "my simple string"
    string2 = "my string"
    string_len = len(string)
    name = "nameless"
    sio = io.StringIO(string2)
    reader = parser.ParseReader(sio, name)
    result = reader.consume_string(parser.StringPredicate(string), string_len, string_len)
    self.assertEqual(result.parse_kind, 'error')
    self.assertEqual(result.error, "expected bytestring `{}'".format(string))
    self.assertEqual(result.causes[0].error, 'unexpected eof')
