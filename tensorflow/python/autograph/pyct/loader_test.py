# coding=utf-8
# Copyright 2017 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Tests for loader module."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import textwrap

import gast

from tensorflow.python.autograph.pyct import loader
from tensorflow.python.autograph.pyct import parser
from tensorflow.python.platform import test
from tensorflow.python.util import tf_inspect


class LoaderTest(test.TestCase):

  def test_parse_load_identity(self):

    def test_fn(x):
      a = True
      b = ''
      if a:
        b = (x + 1)
      return b

    node, _ = parser.parse_entity(test_fn, future_features=())
    module, _, _ = loader.load_ast(node)

    # astunparse uses fixed 4-space indenting.
    self.assertEqual(
        textwrap.dedent(tf_inspect.getsource(test_fn)),
        tf_inspect.getsource(module.test_fn).replace('    ', '  '))

  def test_load_ast(self):
    node = gast.FunctionDef(
        name='f',
        args=gast.arguments(
            args=[
                gast.Name(
                    'a', ctx=gast.Param(), annotation=None, type_comment=None)
            ],
            posonlyargs=[],
            vararg=None,
            kwonlyargs=[],
            kw_defaults=[],
            kwarg=None,
            defaults=[]),
        body=[
            gast.Return(
                gast.BinOp(
                    op=gast.Add(),
                    left=gast.Name(
                        'a',
                        ctx=gast.Load(),
                        annotation=None,
                        type_comment=None),
                    right=gast.Constant(1, kind=None)))
        ],
        decorator_list=[],
        returns=None,
        type_comment=None)

    module, source, _ = loader.load_ast(node)

    expected_source = """
      # coding=utf-8
      def f(a):
          return (a + 1)
    """
    self.assertEqual(
        textwrap.dedent(expected_source).strip(),
        source.strip())
    self.assertEqual(2, module.f(1))
    with open(module.__file__, 'r') as temp_output:
      self.assertEqual(
          textwrap.dedent(expected_source).strip(),
          temp_output.read().strip())

  def test_load_source(self):
    test_source = textwrap.dedent(u"""
      # coding=utf-8
      def f(a):
        '????????? ??????? ??? ????????????? + ???Q(s???, a???)(r??? + ??????????? max Q(???))'
        return a + 1
    """)
    module, _ = loader.load_source(test_source, delete_on_exit=True)
    self.assertEqual(module.f(1), 2)
    self.assertEqual(
        module.f.__doc__, '????????? ??????? ??? ????????????? + ???Q(s???, a???)(r??? + ??????????? max Q(???))')


if __name__ == '__main__':
  test.main()
