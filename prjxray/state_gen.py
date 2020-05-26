#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

from prjxray import util


class StateGen(object):
    """ Manages fuzzer state generation across multiple sites.

    sites - List of sites.
    states_per_site - Maximum number of states used per site.

    If states_per_site is too small, next_state may throw AssertionError.

    StateGen should be used as a iterator for the sites given.  Call next_state
    within each site output loop.  Once 'next' is called on StateGen, StateGen
    will advance state output to the correct position, even if next_state was
    called less than states_per_site.

    """

    def __init__(self, sites, states_per_site):
        self.sites = sites
        self.states_per_site = states_per_site
        self.curr_site_idx = 0
        self.curr_state = None
        self.states = None
        self.curr_site = None

    def __iter__(self):
        assert self.curr_state is None
        assert self.states is None
        assert self.curr_state is None

        self.curr_site_idx = 0
        self.curr_state = None
        self.states = util.gen_fuzz_states(
            len(self.sites) * self.states_per_site)
        self.curr_site = iter(self.sites)
        return self

    def __next__(self):
        next_site = next(self.curr_site)
        self.curr_site_idx += 1

        if self.curr_state is not None:
            while self.curr_state < self.states_per_site:
                self.next_state()

            assert self.curr_state == self.states_per_site, self.curr_state

        self.curr_state = 0

        return next_site

    def next_state(self):
        """ Returns next state within site.

        Should only be called states_per_site for each site.
        """
        self.curr_state += 1

        try:
            state = next(self.states)
        except StopIteration:
            assert False, "Insufficent states, at state {} for site {}".format(
                self.curr_state, self.curr_site_idx)

        return state
