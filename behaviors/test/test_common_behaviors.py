"""Unit test for behaviors.py module."""

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

import py_trees as pt
from behaviors import common_behaviors


def test_sequence_with_memory():
    """Test sequence with memory."""
    root, _ = common_behaviors.get_node('sm(')
    root.add_child(pt.behaviours.TickCounter(1))
    root.add_child(pt.behaviours.Success('Reached second child'))
    root.tick_once()
    assert root.status.value == "RUNNING"
    root.tick_once()
    assert root.status.value == "SUCCESS"


def test_sequence_without_memory():
    """Test sequence without memory."""
    root, _ = common_behaviors.get_node('s(')
    root.add_child(pt.behaviours.TickCounter(1))
    root.add_child(pt.behaviours.Success('Reached second child'))
    root.tick_once()
    assert root.status.value == "RUNNING"
    root.tick_once()
    assert root.status.value == "SUCCESS"

    root, _ = common_behaviors.get_node('s(')
    root.add_child(pt.behaviours.TickCounter(1))
    root.add_child(pt.behaviours.TickCounter(1))

    for _ in range(6):
        root.tick_once()
        assert root.status.value == "RUNNING"


def test_fallback_with_memory():
    """Test fallback with memory."""
    root, _ = common_behaviors.get_node('fm(')
    root.add_child(pt.behaviours.TickCounter(1, "ticker1", pt.common.Status.FAILURE))
    root.add_child(pt.behaviours.TickCounter(1, "ticker2"))
    root.tick_once()
    assert root.status.value == "RUNNING"
    root.tick_once()
    assert root.status.value == "RUNNING"
    root.tick_once()
    assert root.status.value == "SUCCESS"


def test_fallback_without_memory():
    """Test fallback without memory."""
    root, _ = common_behaviors.get_node('f(')
    root.add_child(pt.behaviours.TickCounter(1, "ticker1", pt.common.Status.FAILURE))
    root.add_child(pt.behaviours.TickCounter(1, "ticker2"))

    for _ in range(6):
        root.tick_once()
        assert root.status.value == "RUNNING"


def test_fallback_random():
    """Test random selector."""
    root, _ = common_behaviors.get_node('fr(')
    root.add_child(pt.behaviours.TickCounter(1, 'first ticker', pt.common.Status.FAILURE))
    root.add_child(pt.behaviours.TickCounter(1, 'second ticker', pt.common.Status.SUCCESS))

    # in case the random fallback ticks the FIRST child:
    #   since it returns FAILURE, the tree will then tick the SECOND child.
    #   the execution will thus be:
    #       RUNNING (tick first)
    #       RUNNING (first fails --> tick second)
    #       SUCCESS (second succeeds)
    # in case the random fallback ticks the SECOND child:
    #   since it returns SUCCESS, the execution will thus be:
    #       RUNNING (tick second)
    #       SUCCESS (second succeeds)
    #       RUNNING (root, then random child ticked again)
    status_sequence = []
    for _ in range(3):
        root.tick_once()
        status_sequence.append(root.status.value)

    assert status_sequence == ['RUNNING', 'SUCCESS', 'RUNNING'] or\
        status_sequence == ['RUNNING', 'RUNNING', 'SUCCESS']

    running_ctr = 0
    success_ctr = 0
    other_ctr = 0
    for _ in range(50):
        for _ in range(3):
            root.tick_once()
        if root.status == pt.common.Status.SUCCESS:
            success_ctr += 1
        elif root.status == pt.common.Status.RUNNING:
            running_ctr += 1
        else:
            other_ctr += 1
        root.stop()
    # both counter should be roughly around 25 (50% each)
    assert running_ctr >= 20 and success_ctr >= 20
    # never return FAILURE or INVALID
    assert other_ctr == 0


def test_parallell():
    """Test parallell node."""
    root, _ = common_behaviors.get_node('p(')
    root.add_child(pt.behaviours.TickCounter(1, 'first ticker', pt.common.Status.SUCCESS))
    root.add_child(pt.behaviours.TickCounter(1, 'second ticker', pt.common.Status.SUCCESS))
    for _ in range(2):
        root.tick_once()
    assert root.status == pt.common.Status.SUCCESS
