#!/usr/bin/env python

import sys
import math

from gsp import GSP
from util import argmax_index, ctr

class phadyBB:
    """Balanced bidding agent"""
    # pjh: has properties id, value, and budget
    def __init__(self, id, value, budget):
        self.id = id
        self.value = value
        self.budget = budget

    # pjh: could optimize initial bid, possibly using reserve info
    def initial_bid(self, reserve):
        return self.value / 2

    # pjh: we'll use the info produced by this command
    def slot_info(self, t, history, reserve):
        """Compute the following for each slot, assuming that everyone else
        keeps their bids constant from the previous rounds.

        Returns list of tuples [(slot_id, min_bid, max_bid)], where
        min_bid is the bid needed to tie the other-agent bid for that slot
        in the last round.  If slot_id = 0, max_bid is 2* min_bid.
        Otherwise, it's the next highest min_bid (so bidding between min_bid
        and max_bid would result in ending up in that slot)
        """
        prev_round = history.round(t-1)
        other_bids = filter(lambda (a_id, b): a_id != self.id, prev_round.bids)

        # pjh: must be clicks for each slot
        clicks = prev_round.clicks

        # pjh: the bid_range_for_slot function (in GSP) does most of the work
        def compute(s):
            (min, max) = GSP.bid_range_for_slot(s, clicks, reserve, other_bids)
            if max == None:
                max = 2 * min
            return (s, min, max)

        # gets bid range for each slot
        info = map(compute, range(len(clicks)))
#        sys.stdout.write("slot info: %s\n" % info)
        return info


    def expected_utils(self, t, history, reserve):
        """
        Figure out the expected utility of bidding such that we win each
        slot, assuming that everyone else keeps their bids constant from
        the previous round.

        returns a list of utilities per slot.
        """

        info = self.slot_info(t, history, reserve)

        utilities = map(lambda j: ctr(t,j)*(self.value - ( info[j][1] + 1 ) ), range(len(info)))

        return utilities

    # pjh: just takes the highest expected util slot
    def target_slot(self, t, history, reserve):
        """Figure out the best slot to target, assuming that everyone else
        keeps their bids constant from the previous rounds.

        Returns (slot_id, min_bid, max_bid), where min_bid is the bid needed to tie
        the other-agent bid for that slot in the last round.  If slot_id = 0,
        max_bid is min_bid * 2
        """
        i =  argmax_index(self.expected_utils(t, history, reserve))
        info = self.slot_info(t, history, reserve)
        return info[i]

    def bid(self, t, history, reserve):
        # The Balanced bidding strategy (BB) is the strategy for a player j that, given
        # bids b_{-j},
        # - targets the slot s*_j which maximizes his utility, that is,
        # s*_j = argmax_s {clicks_s (v_j - t_s(j))}.
        # - chooses his bid b' for the next round so as to
        # satisfy the following equation:
        # clicks_{s*_j} (v_j - t_{s*_j}(j)) = clicks_{s*_j-1}(v_j - b')
        # (p_x is the price/click in slot x)
        # If s*_j is the top slot, bid the value v_j

        prev_round = history.round(t-1)
        (slot, min_bid, max_bid) = self.target_slot(t, history, reserve)

        # TODO: Fill this in.
        bid = 0  # change this

        # not expecting to win
        if min_bid > self.value:
            bid = self.value
        # otherwise
        elif slot != 0:
            # ratio of ctr is the same as ratio of positional effect
            bid = self.value - ( ctr(t,slot)/ctr(t,slot-1) ) * ( self.value - (min_bid + 1) )
        else:
            bid = self.value

        # pjh: we've got the target, just need to choose bid to
        # satsify the equation above
        # if t == 47:
        #     print("New Agent:")
        #     print(self.id)
        #     print(t)
        #     print(history.agents_spent[self.id])
        #     print()

        return bid

    # pjh: not sure what this does, but don't think we need to know
    def __repr__(self):
        return "%s(id=%d, value=%d)" % (
            self.__class__.__name__, self.id, self.value)
