"""Test script to visualize or run a py_tree Behavior Tree."""

# Copyright (c) 2022, ABB
# All rights reserved.
#
# Redistribution and use in source and binary forms, with
# or without modification, are permitted provided that
# the following conditions are met:
#
#   * Redistributions of source code must retain the
#     above copyright notice, this list of conditions
#     and the following disclaimer.
#   * Redistributions in binary form must reproduce the
#     above copyright notice, this list of conditions
#     and the following disclaimer in the documentation
#     and/or other materials provided with the
#     distribution.
#   * Neither the name of ABB nor the names of its
#     contributors may be used to endorse or promote
#     products derived from this software without
#     specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import os

import py_trees


dir_path = os.path.dirname(os.path.realpath(__file__))
log_path = os.path.join(dir_path, 'logs')
if not os.path.exists(log_path):
    os.makedirs(log_path)


def build_bt():
    # We can use just Dummy nodes as we do not need to execute but just display.
    condition = py_trees.behaviours.Dummy(name = 'Scene Clear?')
    action = py_trees.behaviours.Dummy(name = 'Disambiguate!')
    disambiguate = py_trees.composites.Selector(name = 'Fallback')
    disambiguate.add_children([condition, action])

    manipulation_task = py_trees.composites.ShrinkedTree(name = 'Manipulation Task!')

    root = py_trees.composites.Sequence(name='Sequence', memory=False)
    root.add_children([disambiguate, manipulation_task])

    return root


def main():
    """Entry point for the demo script."""
    py_trees.pt_logging.level = py_trees.pt_logging.Level.DEBUG

    root = build_bt()

    behaviour_tree = py_trees.trees.BehaviourTree(root)
    py_trees.display.render_dot_tree(
        behaviour_tree.root, name='hri', target_directory=log_path)


if __name__ == '__main__':
    main()
