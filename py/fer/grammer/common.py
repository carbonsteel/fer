
from __future__ import absolute_import
import keyword

def kebab_to_camel(t): # or how to undigest a desert animal
  parts = []
  for w in t.split("-"):
    parts.append(w[0].upper())
    parts.extend(w[1:])
  return "".join(parts)
def kebab_to_snake(t):
  return "_".join(t.split("-"))

def id_to_var(id):
  _id = kebab_to_snake(id)
  if keyword.iskeyword(_id):
    raise ValueError("Can not use a python keyword as variable: {}".format(_id))
  return _id

def id_to_def(id):
  _id = kebab_to_camel(id)
  if keyword.iskeyword(_id):
    raise ValueError("Can not use a python keyword as definition: {}".format(_id))
  return _id

def id_to_parse(id):
  return "_parse_"+kebab_to_snake(id)