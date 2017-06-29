
def kebab_to_camel(t): # or how to undigest a desert animal
  parts = []
  for w in t.split("-"):
    parts.append(w[0].upper())
    parts.extend(w[1:])
  return "".join(parts)
def kebab_to_snake(t):
  return "_".join(t.split("-"))

def id_to_def(id):
  return kebab_to_camel(id)
def id_to_parse(id):
  return "parse_"+kebab_to_snake(id)