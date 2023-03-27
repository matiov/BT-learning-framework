"""Unit test for behavior_lists.py module."""

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

import random
import pytest

from behaviors import behavior_list_test_settings, behavior_lists

behavior_list = behavior_lists.BehaviorLists(
    condition_nodes=behavior_list_test_settings.get_condition_nodes(),
    action_nodes=behavior_list_test_settings.get_action_nodes()
)


def test_random_range():
    """Test the random_range function."""
    assert behavior_lists.random_range(0, 1000, 0) == 0

    random_numbers = []
    for _ in range(100):
        random_numbers.append(behavior_lists.random_range(0, 10, 1))

    assert max(random_numbers) == 10
    assert min(random_numbers) == 0


def test_init():
    """Test the is_condition_node function."""
    _ = behavior_lists.BehaviorLists(fallback_nodes=['f('], sequence_nodes=['s('])


def test_merge():
    """Test the merge BehaviorLists function."""
    new_behavior_list = behavior_lists.BehaviorLists(
        condition_nodes=[behavior_lists.ParameterizedNode('condition1', None, [], True)],
        action_nodes=[behavior_lists.ParameterizedNode('action1', None, [], False)]
    )

    behavior_list.merge_behaviors(new_behavior_list)
    assert new_behavior_list.condition_nodes[0] in behavior_list.condition_nodes
    assert new_behavior_list.action_nodes[0] in behavior_list.action_nodes


def test_is_fallback_node():
    """Test the is _fallback_node function."""
    assert behavior_list.is_fallback_node('f(')
    assert not behavior_list.is_fallback_node('s(')


def test_is_sequence_node():
    """Test the is_sequence_node function."""
    assert not behavior_list.is_sequence_node('f(')
    assert behavior_list.is_sequence_node('s(')


def test_get_random_control_node():
    """Test the get_random_Control_node function."""
    for _ in range(10):
        assert behavior_list.is_control_node(behavior_list.get_random_control_node())


def test_get_random_condition_node():
    """Test the get_random_condition_node function."""
    for _ in range(10):
        assert behavior_list.is_condition_node(behavior_list.get_random_condition_node())


def test_get_random_behavior_node():
    """Test the get_random_behavior_node function."""
    for _ in range(10):
        assert behavior_list.is_behavior_node(behavior_list.get_random_behavior_node())


def test_get_random_leaf_node():
    """Test the get_random_leaf_node function."""
    for _ in range(10):
        assert behavior_list.is_leaf_node(behavior_list.get_random_leaf_node())


def test_set_random_value():
    """Test the set_random_value function."""
    parameter = behavior_lists.NodeParameter([], 0, 1, 1)
    parameter.set_random_value()
    assert parameter.value in (0, 1)

    parameter = behavior_lists.NodeParameter(
        [], (0, 1, 2), (1, 3, 5), (1, 2, 3), data_type=behavior_lists.ParameterTypes.POSITION)
    parameter.set_random_value()
    assert parameter.value[0] in (0, 1)
    assert parameter.value[1] in (1, 3)
    assert parameter.value[2] in (2, 5)

    parameter = behavior_lists.NodeParameter(
        [], (0, 1, 2), (1, 3, 5), data_type=behavior_lists.ParameterTypes.POSITION)
    parameter.set_random_value()
    assert 0 <= parameter.value[0] <= 1
    assert 1 <= parameter.value[1] <= 3
    assert 2 <= parameter.value[2] <= 5

    parameter = behavior_lists.NodeParameter(
        [], 0, 1, data_type=behavior_lists.ParameterTypes.FLOAT)
    parameter.set_random_value()
    assert 0 <= parameter.value <= 1

    random.seed(10)
    parameter = behavior_lists.NodeParameter(data_type=behavior_lists.ParameterTypes.STRING)
    parameter.set_random_value()
    assert 'upuh3' == parameter.value

    parameter = behavior_lists.NodeParameter([], data_type=-1)
    with pytest.raises(Exception):
        parameter.set_random_value()


def test_add_random_parameters():
    """Test the add_random_parameters function."""
    parameters = [behavior_lists.NodeParameter([0, 1])]
    node = behavior_lists.ParameterizedNode('a', None, parameters=parameters, comparing=True)
    node.add_random_parameters()
    assert node.parameters[0].value in (0, 1)  # pylint: disable=unsubscriptable-object
    assert node.larger_than in (True, False)


def test_get_parameters():
    """Test the get_parameters function."""
    parameters = [behavior_lists.NodeParameter(value=0), behavior_lists.NodeParameter(value=1)]
    node = behavior_lists.ParameterizedNode('a', None, parameters=parameters)
    assert node.get_parameters() == [0, 1]


def test_to_string():
    """Test the to_string function."""
    node = behavior_lists.ParameterizedNode('a')
    assert node.to_string() == 'a?'

    node = behavior_lists.ParameterizedNode('a', condition=False)
    assert node.to_string() == 'a!'

    parameters = [behavior_lists.NodeParameter(value=0)]
    node = behavior_lists.ParameterizedNode('a', parameters=parameters)
    assert node.to_string() == 'a 0?'

    parameters = [behavior_lists.NodeParameter(
        data_type=behavior_lists.ParameterTypes.FLOAT, value=0.1)]
    node = behavior_lists.ParameterizedNode('a', parameters=parameters)
    assert node.to_string() == 'a 0.1?'

    parameters = [behavior_lists.NodeParameter(
        data_type=behavior_lists.ParameterTypes.POSITION, value=(0.1, 0.2, 0.3))]
    node = behavior_lists.ParameterizedNode('a', parameters=parameters)
    assert node.to_string() == 'a (0.1, 0.2, 0.3)?'

    parameters = [behavior_lists.NodeParameter(value=0)]
    node = behavior_lists.ParameterizedNode('a', parameters=parameters, comparing=True)
    assert node.to_string() == 'a > 0?'

    parameters = [behavior_lists.NodeParameter(value=0)]
    node = behavior_lists.ParameterizedNode(
        'a', parameters=parameters, comparing=True, larger_than=False)
    assert node.to_string() == 'a < 0?'

    parameters = [behavior_lists.NodeParameter(value=0, placement=0)]
    node = behavior_lists.ParameterizedNode('a', parameters=parameters)
    assert node.to_string() == '0 a?'

    parameters = [behavior_lists.NodeParameter(value=0, placement=1)]
    node = behavior_lists.ParameterizedNode('ab', parameters=parameters)
    assert node.to_string() == 'a 0 b?'
