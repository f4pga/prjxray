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

from collections import namedtuple


def check_signed_range(min_value, max_value, bits):
    """

    Check if fits in signed range, saving 1 value for sentinel.

    >>> check_signed_range(-127, 127, 8)
    True
    >>> check_signed_range(-128, 128, 8)
    False
    >>> check_signed_range(-32767, 32767, 16)
    True
    >>> check_signed_range(-32768, 32768, 16)
    False

    """
    assert bits / 2 == bits // 2
    return min_value >= -(2**(bits // 2) - 1) and max_value <= (
        (2**(bits // 2)) - 1)


def get_sentinel(attr):
    if attr == 'u1':
        return 2
    if attr == 'u8':
        return 2**8 - 1
    elif attr == 'u16':
        return 2**16 - 1
    elif attr == 'u32':
        return 2**32 - 1
    elif attr == 'i8':
        return -(2**8)
    elif attr == 'i16':
        return -(2**15)
    elif attr == 'i32':
        return -(2**31)
    else:
        assert False, attr


class CompactArray():
    def __init__(self):
        self.items = None
        self.item_to_idx = None

    def init_items(self, number_of_items):
        self.items = [None for _ in range(number_of_items)]

    def set_items(self, items):
        self.items = tuple(items)

    def get(self, idx):
        return self.items[idx]

    def build_index(self):
        if self.item_to_idx is None:
            self.item_to_idx = {}
            for idx, item in enumerate(self.items):
                assert item not in self.item_to_idx
                self.item_to_idx[item] = idx

    def index(self, key):
        self.build_index()
        return self.item_to_idx[key]

    def index_get(self, key, default=None):
        self.build_index()
        return self.item_to_idx.get(key, default)

    def read_from_capnp(self, compact_array):
        attr = compact_array.storage.which()
        sentinel = get_sentinel(attr)
        self.items = [
            (item if item != sentinel else None)
            for item in getattr(compact_array.storage, attr)
        ]
        self.item_to_idx = None

    def store_data(self, attr, arr):
        sentinel = get_sentinel(attr)
        for idx, item in enumerate(self.items):
            if item is None:
                arr[idx] = sentinel
            else:
                arr[idx] = item if attr is not 'u1' else item==1

    def write_to_capnp(self, compact_array):
        if len(self.items) > 0:
            min_value = min(item for item in self.items if item is not None)
            max_value = max(item for item in self.items if item is not None)
        else:
            min_value = 0
            max_value = 0

        if min_value >= 0:
            # Unsigned, saving max room for the sentinel value.
            if max_value < 2**1:
                attr = 'u1'
            elif max_value < 2**8 - 1:
                attr = 'u8'
            elif max_value < 2**16 - 1:
                attr = 'u16'
            elif max_value < 2**32 - 1:
                attr = 'u32'
            else:
                assert False, max_value
        else:
            # Signed.
            if check_signed_range(min_value, max_value, 8):
                attr = 'i8'
            elif check_signed_range(min_value, max_value, 16):
                attr = 'i16'
            elif check_signed_range(min_value, max_value, 32):
                attr = 'i32'
            else:
                assert False, (min_value, max_value)

        compact_array.storage.init(attr, len(self.items))
        self.store_data(attr, getattr(compact_array.storage, attr))


class StructOfArrayProxy():
    def __init__(self, struct_of_array, index):
        self.struct_of_array = struct_of_array
        self.index = index

    def __getitem__(self, attr):
        sub_index = self.struct_of_array.field_to_index[attr]

        return self.struct_of_array.items[sub_index].items[self.index]

    def to_tuple(self):
        return self.struct_of_array.namedtuple(
            *(
                self.struct_of_array.items[sub_index].items[self.index]
                for sub_index in range(self.struct_of_array.number_of_fields)))

    def __hash__(self):
        return hash(self.to_tuple())

    def __eq__(self, other):
        return self._asdict() == other._asdict()

    def _asdict(self):
        return self.to_tuple()._asdict()


class StructOfArray():
    def __init__(self, element_name, fields):
        self.namedtuple = namedtuple(element_name, ' '.join(fields))
        self.number_of_fields = len(fields)
        self.field_to_index = {}
        for idx, field in enumerate(fields):
            self.field_to_index[field] = idx
        self.items = None
        self.item_to_idx = None

    def set_items(self, items):
        self.items = []

        for _ in range(self.number_of_fields):
            self.items.append(CompactArray())
            self.items[-1].init_items(len(items))

        for idx, item in enumerate(items):
            assert len(item) == self.number_of_fields

            for field in range(self.number_of_fields):
                self.items[field].items[idx] = item[field]

    def get(self, index):
        return StructOfArrayProxy(self, index)

    def index(self, key):
        if self.item_to_idx is None:
            self.item_to_idx = {}
            for idx in range(len(self.items[0].items)):
                item = self.get(idx)
                assert item not in self.item_to_idx
                self.item_to_idx[item] = idx

        return self.item_to_idx[self.namedtuple(*key)]

    def read_from_capnp(self, compact_arrays):
        assert len(compact_arrays) == self.number_of_fields

        item_counts = set()
        self.items = []
        for compact_array in compact_arrays:
            self.items.append(CompactArray())
            self.items[-1].read_from_capnp(compact_array)

            item_counts.add(len(self.items[-1].items))

        assert len(item_counts) == 1

        self.item_to_idx = None

    def write_to_capnp(self, compact_arrays):
        assert len(compact_arrays) == self.number_of_fields

        for idx, compact_array in enumerate(compact_arrays):
            self.items[idx].write_to_capnp(compact_array)
