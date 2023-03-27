"""
Simple task planner inspired 'Towards Blended Reactive Planning and Acting using Behavior Trees'.

Generates a BT to solve task given a set of goals and behaviors with pre- and post-conditions.
Since the conditions are not always static, it runs the tree while evaluating the conditions.
"""

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

import logging
from typing import Any, List, Tuple

from behaviors.common_behaviors import RSequence, ActionBehavior
from bt_learning.planner.constraints_identification import contains_conflicting
import py_trees as pt
from py_trees.composites import Selector, Sequence


logger = logging.getLogger('lfd-planner')


def handle_precondition(
    precondition: List[str],
    behaviors: Any,
    world_interface: Any
) -> List[pt.trees.BehaviourTree]:
    """Handle pre-condition by exploiting the backchaining method."""
    # print("Condition in: ", precondition)
    condition_parameters = behaviors.get_condition_parameters(precondition)
    trees = []
    best_cost = float('inf')

    action_list = behaviors.get_behavior_list().action_nodes

    for action in action_list:
        action_node, _ = behaviors.get_node(action, world_interface, condition_parameters)

        if precondition in action_node.get_postconditions():
            # Only keep the actions with lowest cost
            if action_node.cost() > best_cost:
                continue
            elif action_node.cost() < best_cost:
                trees.clear()
                best_cost = action_node.cost()

            action_preconditions = action_node.get_preconditions()
            if action_preconditions != []:
                bt = RSequence('Sequence')
                # bt = Sequence('Sequence', memory=False)

                for action_precondition in action_preconditions:
                    child, _ = behaviors.get_node(
                        action_precondition,
                        world_interface,
                        behaviors.get_condition_parameters(action_precondition)
                    )
                    bt.add_child(child)

                bt.add_child(action_node)
            else:
                bt = action_node

            trees.append(bt)
    # print("ERROR, no matching action found to ensure precondition")
    return trees


def extend_leaf_node(
    leaf_node: pt.behaviour.Behaviour,
    behaviors: Any,
    world_interface: Any
) -> None:
    """
    Extend the failing node.

    If leaf node fails, it should be replaced with a selector that checks leaf node
    and a subtree that fixes the condition whenever it's not met.
    """
    bt = Selector(name='Fallback')
    # Make the replacing subtree is still failing. The parent node might get confused
    # if one of its children suddenly changes status to INVALID.
    bt.stop(pt.common.Status.FAILURE)
    leaf_node.parent.replace_child(leaf_node, bt)
    bt.add_child(leaf_node)
    print('What is failing?', leaf_node.name)

    extended = handle_precondition(leaf_node.name, behaviors, world_interface)
    for tree in extended:
        bt.add_child(tree)


def expand_tree(
    node: pt.composites.Composite or pt.behaviour.Behaviour,
    behaviors: Any,
    world_interface: Any,
    depth: int = 0
) -> None:
    """Expand the part of the tree that fails."""
    # print("TREE COMING IN :", node)

    # If the recursion is very deep there is some problem and we should abort
    if depth >= 100:
        logger.warning('Maximum condition expansion depth reached')
        return

    if node.name == 'Fallback':
        # print("Fallback node fails\n")
        for index, child in enumerate(node.children):
            if index >= 1:  # Normally there will only be two children
                expand_tree(child, behaviors, world_interface, depth+1)
    elif node.name == 'Sequence' or node.name == 'RandomSelector':
        # print("Sequence node fails\n")
        for i in range(len(node.children)):
            if node.children[i].status == pt.common.Status.FAILURE:
                # print("Child that fails: ", node.children[i].name)
                expand_tree(node.children[i], behaviors, world_interface, depth+1)
    elif isinstance(node, pt.behaviour.Behaviour) and node.status == pt.common.Status.FAILURE:
        extend_leaf_node(node, behaviors, world_interface)
    # else:
        # print("Tree", node.name)


def get_tree_effects(tree: pt.trees.BehaviourTree) -> List[str]:
    """
    Return all effects of a tree as action strings.

    I.e. traverses the tree and returns the first child of each fallback node,
    and the postconditions of the last child of each sequence node.
    """
    if isinstance(tree, ActionBehavior):
        effects = tree.get_postconditions()
    elif len(tree.children) > 0:
        conditions = []
        for child in tree.children:
            conditions += get_tree_effects(child)
        effects = conditions
    else:
        effects = []

    return effects


def conflicting_subtrees(
    trees: List[pt.trees.BehaviourTree],
    behaviors: Any
) -> Tuple[int, int]:
    """
    Return the indices of the conflicting subtrees in the list trees.

    It returns (-1, -1) if there are no conflicts.
    It is assumed that each element of trees is a fallback node or a condition node.
    """
    for i in range(len(trees)-2, -1, -1):
        if isinstance(trees[i], Selector) and not\
           (isinstance(trees[i], RSequence) or isinstance(trees[i], Sequence)):
            # The condition is the first child of a fallback node
            high_priority_condition = trees[i].children[0].name
        else:
            high_priority_condition = trees[i].name

        for j in range(i+1, len(trees)):
            effects = get_tree_effects(trees[j])
            if contains_conflicting(behaviors, effects, high_priority_condition):
                return i, j

    return -1, -1


def handle_priority(
    tree: pt.trees.BehaviourTree,
    behaviors: Any
) -> bool:
    """Detect subtrees that have conflicting effects and reorders them."""
    if isinstance(tree, RSequence) or isinstance(tree, Sequence):
        subtrees = tree.children
        # The last child of all sequence nodes is an action node except
        # for the topmost sequence node that contains all goal conditions.
        # Don't include the last child unless it is the topmost node
        i, j = conflicting_subtrees(subtrees, behaviors)

        n_tries = 0
        while i != -1:
            logger.info('Detected conflicting subtrees')
            logger.debug(
                'Conflicting subtrees:\n%s-----------------\n%s',
                pt.display.unicode_tree(subtrees[i]),
                pt.display.unicode_tree(subtrees[j])
            )
            # Place child j before child i
            tree_to_move = subtrees[j]
            tree.remove_child(tree_to_move)
            tree.insert_child(tree_to_move, i)

            i, j = conflicting_subtrees(subtrees, behaviors)

            n_tries += 1
            if n_tries > len(subtrees):
                logger.warning(
                    'Could not find a configuration of subtrees without conflicting effects')
                return False

        return True

    for child in tree.children:
        if not handle_priority(child, behaviors):
            return False
    return True


def plan(
    world_interface: Any,
    behaviors: Any,
    tree: pt.trees.BehaviourTree
) -> pt.trees.BehaviourTree:
    """
    Generate a BT to solve a task given: initial tree and behaviors with pre- and post-conditions.

    Since the conditions are not always static, it runs the tree while evaluating the conditions.
    """
    # print(pt.display.unicode_tree(root=tree, show_status=True))
    for _ in range(100):
        if not handle_priority(tree, behaviors):
            break
        tree.tick_once()
        # print("Tick: ", i)
        # print(pt.display.unicode_tree(root=tree, show_status=True))
        if tree.status is pt.common.Status.FAILURE:
            expand_tree(tree, behaviors, world_interface)
            # print(pt.display.unicode_tree(root=tree, show_status=True))
        elif tree.status is pt.common.Status.SUCCESS:
            break

    return tree
