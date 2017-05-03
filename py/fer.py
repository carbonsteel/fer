#!/usr/bin/python2

import grammar
import ferparser
import io

if __name__ == "__main__":
  with io.open("test.fer", "rb") as f:
    brf = io.BufferedReader(f)
    r = grammar.ParseReader(brf)
    gp = ferparser.FerParser(r)
    result = gp()
    r.consume_ws()
    eof_result = r.consume_eof()
    if not eof_result:
      result.put(causes=[eof_result])
    print grammar.pformat(r.stats)
    print grammar.pformat(result)