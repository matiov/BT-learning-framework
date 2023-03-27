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

import functools
import os

import py_trees


dir_path = os.path.dirname(os.path.realpath(__file__))
log_path = os.path.join(dir_path, 'logs')
if not os.path.exists(log_path):
    os.makedirs(log_path)


def pre_tick_handler(behaviour_tree: py_trees.trees.BehaviourTree):
    """
    This prints a banner and will run immediately before every tick of the tree.

    Args:
    ----
        behaviour_tree (:class:`~py_trees.trees.BehaviourTree`): the tree custodian.

    """
    print("\n--------- Run %s ---------\n" % behaviour_tree.count)


def post_tick_handler(snapshot_visitor, behaviour_tree):
    """Prints an ascii tree with the current snapshot status."""
    print(
        "\n" + py_trees.display.unicode_tree(
            root = behaviour_tree.root,
            visited = snapshot_visitor.visited,
            previously_visited = snapshot_visitor.previously_visited
        )
    )
    name_ = 'root' + str(behaviour_tree.count)
    py_trees.display.render_dot_tree(
        behaviour_tree.root, name=name_, target_directory=log_path, static=False)


def demo1_bt():
    task_one = py_trees.behaviours.Count(
        name = 'Task 1',
        fail_until = 0,
        running_until = 2,
        success_until = 10
    )
    task_two = py_trees.behaviours.Count(
        name = 'Task 2',
        fail_until = 0,
        running_until = 2,
        success_until = 10
    )
    high_priority_interrupt = py_trees.decorators.RunningIsFailure(
        child = py_trees.behaviours.Periodic(
            name = 'High Priority',
            n = 3
        )
    )
    piwylo = py_trees.idioms.pick_up_where_you_left_off(
        name = 'Pick Up\nWhere You\nLeft Off',
        tasks = [task_one, task_two]
    )
    root = py_trees.composites.Selector(name='Root')
    root.add_children([high_priority_interrupt, piwylo])

    return root


def run_demo1():
    root = demo1_bt()

    behaviour_tree = py_trees.trees.BehaviourTree(root)
    behaviour_tree.add_pre_tick_handler(pre_tick_handler)
    behaviour_tree.visitors.append(py_trees.visitors.DebugVisitor())
    snapshot_visitor = py_trees.visitors.SnapshotVisitor()
    behaviour_tree.add_post_tick_handler(functools.partial(post_tick_handler, snapshot_visitor))
    behaviour_tree.visitors.append(snapshot_visitor)
    behaviour_tree.setup(timeout=15)
    py_trees.display.render_dot_tree(behaviour_tree.root, name='static', target_directory=log_path)

    for unused_i in range(1, 11):
        behaviour_tree.tick()

    print("\n")


def main():
    """Entry point for the demo script."""
    py_trees.pt_logging.level = py_trees.pt_logging.Level.DEBUG

    run_demo1()


if __name__ == '__main__':
    main()
