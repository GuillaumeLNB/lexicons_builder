#!/bin/python3
import unittest
import os
import sys

sys.path.insert(0, os.path.join("..", ".."))

from lexicons_builder.nlp_model_explorer.explorer import _load_model as load_model

model = load_model(sys.argv[1])

assert len(model.vocab)
print("ok", file=sys.stderr)
