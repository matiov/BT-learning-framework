"""Test script for Blackboard interaction and visualization."""

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

import py_trees as pt


dir_path = os.path.dirname(os.path.realpath(__file__))
log_path = os.path.join(dir_path, 'logs')
if not os.path.exists(log_path):
    os.makedirs(log_path)


class Condition1(pt.behaviour.Behaviour):

    def __init__(self, name: str = 'Condition'):
        super().__init__(name)
        self.blackboard = self.attach_blackboard_client()
        self.blackboard.register_key(key='bool_var', access=pt.common.Access.WRITE)
        try:
            self.blackboard.bool_var = True
        except KeyError as e:
            raise RuntimeError(f'Blackboard variable "bool_var" not found [{e}].')

    def initialise(self):
        print(f'Reading {self.blackboard.bool_var}')

    def update(self):
        if self.blackboard.bool_var:
            return pt.common.Status.SUCCESS
        else:
            return pt.common.Status.FAILURE


class Action1(pt.behaviour.Behaviour):

    def __init__(self, name: str = 'Action1'):
        super().__init__(name)
        self.blackboard = self.attach_blackboard_client()
        self.blackboard.register_key(key='bool_var', access=pt.common.Access.WRITE)
        self.blackboard.register_key(key='str_var', access=pt.common.Access.READ)

        self.counter = 0

    def update(self):
        print(f'Reading {self.blackboard.str_var}.')
        if self.counter > 2:
            self.blackboard.bool_var = True
            print('Updating bool variable')
            return pt.common.Status.SUCCESS
        else:
            self.counter += 1
            return pt.common.Status.RUNNING


class Action2(pt.behaviour.Behaviour):

    def __init__(self, name: str = 'Action2'):
        super().__init__(name)
        self.blackboard = self.attach_blackboard_client()
        self.blackboard.register_key(key='bool_var', access=pt.common.Access.WRITE)
        self.blackboard.register_key(key='str_var', access=pt.common.Access.WRITE)

        self.counter = 0

    def initialise(self):
        # This function is run once every tick!!
        self.blackboard.str_var = 'TARGET'

    def update(self):
        if self.counter == 2:
            self.counter += 1
            self.blackboard.bool_var = False
            return pt.common.Status.FAILURE
        elif self.counter > 4 and self.blackboard.bool_var is True:
            return pt.common.Status.SUCCESS
        else:
            self.counter += 1
            return pt.common.Status.RUNNING


def pre_tick_handler(behaviour_tree: pt.trees.BehaviourTree):
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
        "\n" + pt.display.unicode_tree(
            root = behaviour_tree.root,
            visited = snapshot_visitor.visited,
            previously_visited = snapshot_visitor.previously_visited
        )
    )
    name_ = 'blackboard' + str(behaviour_tree.count)
    pt.display.render_dot_tree(
        behaviour_tree.root,
        name=name_,
        target_directory=log_path,
        with_blackboard_variables=True,
        static=False
    )


def build_bt():
    # We can use just Dummy nodes as we do not need to execute but just display.
    condition = Condition1()
    action1 = Action1()
    subtree = pt.composites.Selector(name = 'Fallback', memory=False)
    subtree.add_children([condition, action1])

    action2 = Action2()

    root = pt.composites.Sequence(name='Sequence', memory=False)
    root.add_children([subtree, action2])

    return root


def run_demo():
    root = build_bt()

    behaviour_tree = pt.trees.BehaviourTree(root)
    behaviour_tree.add_pre_tick_handler(pre_tick_handler)
    behaviour_tree.visitors.append(pt.visitors.DebugVisitor())
    snapshot_visitor = pt.visitors.SnapshotVisitor()
    behaviour_tree.add_post_tick_handler(functools.partial(post_tick_handler, snapshot_visitor))
    behaviour_tree.visitors.append(snapshot_visitor)
    behaviour_tree.setup(timeout=15)
    pt.display.render_dot_tree(
        behaviour_tree.root,
        name='static',
        target_directory=log_path,
        with_blackboard_variables=True
    )

    clients = pt.blackboard.Blackboard.clients
    print(clients.items())

    for unused_i in range(1, 11):
        behaviour_tree.tick()

    print("\n")


def main():
    """Entry point for the demo script."""
    pt.pt_logging.level = pt.pt_logging.Level.DEBUG

    run_demo()


if __name__ == '__main__':
    main()
