#!/bin/bash
gprof2dot -f pstats "$1" > "$1".dot \
  && dot -Tpng -o "$1".png "$1".dot \
  && exec xdot "$1".dot