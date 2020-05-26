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
""" Route timing delay definitions.
Routing delay is formed from two parts in this model:

- Intristic delay of the element
- Capactive loading delay of the net

Intristic delay is a time value (e.g. nanoseconds), does not vary based on
routing fanout.  It does vary based on the PVT (process, voltage, temperature)
corner.  PvtCorner and IntristicDelay objects are used to model intristic
delay of elements.

Capactive loading is the elmore delay from the RC tree formed by interconnect.
The RC tree is made up of 5 types of RC nodes:


|Element type          |Object        |Intrinsic delays?|Output resistance?|Capacitance type    |
|----------------------|--------------|-----------------|------------------|--------------------|
|Site output pin       |Outpin        |Yes              |Yes               |N/A                 |
|Buffered switch       |Buffer        |Yes              |Yes               |Internal capacitance|
|Pass-transistor switch|PassTransistor|Yes              |Yes               |N/A                 |
|Wire                  |Wire          |No               |Yes               |Pi model            |
|Site input pin        |Inpin         |Yes              |No                |Input capacitance   |

The elmore delay is the RC tree formed by these 5 components.  Out pins and
buffer switches are the roots of the elmore tree. Buffer switches
and inpins are leafs of the elmore tree. Wires and pass-transistor switches are
nodes in the tree. Wires share their capacitance upstream and downstream using
a pi-model.

Example timing tree:

    +------+
    |Outpin|
    +--+---+
    |
    |
    v
    +--+--+
    |Wire |
    +--+--+
    |
    +-----------------+
    |                 |
    +--+---+     +-------+------+
    |Buffer|     |PassTransistor|
    +--+---+     +------+-------+
    |                |
    v                v
    +--+-+           +--+-+
    |Wire|           |Wire|
    +--+-+           +--+-+
    |                |
    v                v
    +--+--+          +--+--+
    |Inpin|          |Inpin|
    +-----+          +-----+

Note on units:

The timing model operates on the following types of units:
 - Time
 - Resistance
 - Capacitance

For a consistent unit set, the following equation must be satisfied:

1 Resistance unit * 1 Capacitance unit = 1 Time unit

The SI unit set would be:
 - Time = seconds
 - Resistance = Ohms
 - Capacitance = Farads

However as long as the scale factors are consistent, the model will work
with other unit combinations.  For example:
 - Time = nanoseconds (1e-9 seconds)
 - Resistance = milliOhms (1e-3 Ohms)
 - Capacitance = microFarads (1e-6 Farads)

(1e-3 * 1e-6) (Ohms * Farads) does equal (1e-9) seconds.

"""
import enum
from collections import namedtuple


class PvtCorner(enum.Enum):
    """ Process/voltage/temperature corner definitions. """

    # Corner where device operates with fastest intristic delays.
    FAST = "FAST"

    # Corner where device operates with slowest intristic delays.
    SLOW = "SLOW"

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented


class IntristicDelay(namedtuple('IntristicDelay', 'min max')):
    """ An intristic delay instance.

    Represents is the intristic delay through an element (e.g. a site pin or
    interconnect pip).

    The intristic delay of an element is generally modelled at a particular
    "corner" of a design.  The "corner" generally speaking is modelled over
    process, voltage and temperature PVT.  The IntristicDelay object
    reperesents the minimum or maximum delay through all instances of the
    element at 1 corner.

    Attributes
    ----------

    min : float
        Minimum instrinsic delay (nsec)

    max : float
        Maximum instrinsic delay (nsec)
    """


class RcElement(namedtuple('RcElement', 'resistance capacitance')):
    """ One part of an RcNode, embedded within an RcTree.

    Attributes
    ----------

    resistance : float
        Resistance of element

    capacitance : float
        Capacitance of element

    """
    pass


class hashabledict(dict):
    """ Immutable version of dictionary with hash support. """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hash = hash(tuple(sorted(self.items())))

    def setdefault(self, *args, **kwargs):
        raise NotImplementedError("hashabledict cannot be mutated.")

    def __setitem__(self, *args, **kwargs):
        raise NotImplementedError("hashabledict cannot be mutated.")

    def update(self, *args, **kwargs):
        raise NotImplementedError("hashabledict cannot be mutated.")

    def __hash__(self):
        return self.hash


def fast_slow_tuple_to_corners(arr):
    """ Convert delay 4-tuple into two IntristicDelay objects.

    Returns
    -------

    corners : dict of PvtCorner to IntristicDelay
        Dictionary keys of FAST and SLOW, mapping to the instrinsic delay
        for each corner.

    """

    fast_min, fast_max, slow_min, slow_max = map(float, arr)

    return hashabledict(
        {
            PvtCorner.FAST: IntristicDelay(
                min=fast_min,
                max=fast_max,
            ),
            PvtCorner.SLOW: IntristicDelay(
                min=slow_min,
                max=slow_max,
            ),
        })


class TimingNode(object):
    """ Base class for timing node models.
    """

    def get_intrinsic_delays(self):
        """ Returns Intristic delays (if any) timing node.

        Returns
        -------

        Dictionary of PvtCorner to Intristic. Is None if node has no intristic
        delay.
        """

        pass

    def get_rc_delay(self):
        """ Return portion of net delay due to elmore (RC) delay at this node.

        Must be called after propigate_delays has been called on the Outpin
        object of this tree.

        """
        pass

    def get_downstream_cap(self):
        """ Returns downstream capacitance at this node.

        Must be called after propigate_delays has been called on the Outpin
        object of this tree.

        """
        pass

    def propigate_downstream_capacitance(self, math):
        """ Returns capacitance visible to parent of this node.

        Must call propigate_downstream_capacitance on all children of this node.
        Should save downstream capacitance visible to this node's output
        (if any) to be returned in the get_downstream_cap method.
        """
        pass


class DownstreamNode(TimingNode):
    """ All non-root TimingNode's are DownstreamNode's.

    """

    def propigate_delays(self, elements, math):
        """ Propigates upstream delay elements to children of the tree.

        Must call propigated_delays on all children of this node, and add this
        node to elements.

        Arguments
        ---------
        elements : list of TimingNode's
            List of delay nodes between root of this tree and this node.
        math : MathModel
            Math model to use to compute delays
        """
        pass


class Outpin(TimingNode):
    """ Represents a site output pin.

    Outpin object is the root of the timing tree.  Once tree is built with
    set_sink_wire and Wire.add_child methods, propigate_delays should be
    invoked to estabilish model.

    Arguments
    ---------

    resistance
        Drive resistance in elmore delay model
    delays
        Intristic delays on output pin.

    """

    def __init__(self, resistance, delays):
        self.resistance = resistance
        self.delays = delays
        self.sink_wire = None

        self.downstream_cap = None
        self.rc_delay = None

    def set_sink_wire(self, wire):
        """ Sets sink wire for this output pin.

        An output pin always sinks to exactly 1 wire.

        This method must be called prior to calling propigate_delays method
        on this object.

        Arguments
        ---------
        wire : Wire object
            Sink wire for this output pin.

        """
        self.sink_wire = wire

    def propigate_downstream_capacitance(self, math):
        assert self.sink_wire is not None
        self.downstream_cap = self.sink_wire.propigate_downstream_capacitance(
            math)
        self.rc_delay = math.multiply(self.downstream_cap, self.resistance)

    def propigate_delays(self, math):
        """ Propigate delays throughout tree using specified math model.

        Must be called after elmore tree is estabilished.

        Arguments
        ---------
        math : MathModel object
            Math model used when doing timing computations.

        """
        self.propigate_downstream_capacitance(math)
        self.sink_wire.propigate_delays([self], math)
        self.rc_delay = math.multiply(self.resistance, self.downstream_cap)

    def get_intrinsic_delays(self):
        return self.delays

    def get_rc_delay(self):
        assert self.rc_delay is not None
        return self.rc_delay

    def get_downstream_cap(self):
        assert self.downstream_cap is not None
        return self.downstream_cap


class Inpin(DownstreamNode):
    """ Represents a site input pin.

    Represents leaf of timing model.  Once model is connected and delays
    are propigate (by calling Outpin,propigated_delays), get_delays will
    correctly return the list of delay elements from the root to this leaf.

    Arguments
    ---------

    capacitance
        Pin capacitance for input pin.
    delays
        Intristic delays on input pin.

    """

    def __init__(self, capacitance, delays, name=None):
        self.capacitance = capacitance
        self.delays = delays
        self.propigated_delays = None
        self.name = name

    def get_intrinsic_delays(self):
        return self.delays

    def get_rc_delay(self):
        return None

    def get_downstream_cap(self):
        return None

    def propigate_downstream_capacitance(self, math):
        return self.capacitance

    def propigate_delays(self, elements, math):
        self.propigated_delays = list(elements)

    def get_delays(self):
        """ Return list of delay models that make up the delay for this pin.

        The sum of all delay elements (both intristic and RC) is the net
        delay from the output pin to this input pin.

        """
        return self.propigated_delays + [self]


class Wire(DownstreamNode):
    """ Represents a wire in the timing model.

    Wires must be connected to an upstream driver model (Outpin, Buffer,
    PassTransistor objects) with set_sink_wire, and add_child must be called
    attaching output nodes (Buffer, PassTransistor, Inpin objects).

    Arguments
    ---------
    rc_elements : List of RcElement
        Resistance and capacitance of this wire.
    math : MathModel
        Math model used to compute lumped resistance and capacitance.

    """

    def __init__(self, rc_elements, math):
        self.resistance = math.sum(elem.resistance for elem in rc_elements)
        self.capacitance = math.sum(elem.capacitance for elem in rc_elements)
        self.children = []

        self.downstream_cap = None
        self.propigated_delays = None
        self.rc_delay = None

    def add_child(self, child):
        """ Add a child node to this wire.

        Call this method as needed prior to calling propigate_delays on the
        root Outpin object.

        Arguments
        ---------
        child : Buffer or PassTransistor or Inpin
            Adds child load to this wire.

        """
        self.children.append(child)

    def propigate_downstream_capacitance(self, math):
        downstream_cap = math.sum(
            child.propigate_downstream_capacitance(math)
            for child in self.children)

        # Pi-model is definied such that wire resistance only sees half of the
        # wire capacitance.
        self.downstream_cap = math.plus(
            math.divide(self.capacitance, 2), downstream_cap)

        # Upstream seems all of the wires capacitance
        return math.plus(downstream_cap, self.capacitance)

    def propigate_delays(self, elements, math):
        self.propigated_delays = list(elements)

        for child in self.children:
            child.propigate_delays(self.propigated_delays + [self], math)

        self.rc_delay = math.multiply(self.resistance, self.downstream_cap)

    def get_intrinsic_delays(self):
        return None

    def get_rc_delay(self):
        assert self.rc_delay is not None
        return self.rc_delay

    def get_downstream_cap(self):
        assert self.downstream_cap is not None
        return self.downstream_cap


class Buffer(DownstreamNode):
    """ Represents an isolating switch.

    The internal_capacitance model is such that the upstream node only sees
    the capacitance of this node when the switch is enabled.  Therefore, only
    active buffers should be included in the model.

    Arguments
    ---------
    internal_capacitance
        Capacitance seen by upstream node when this buffer is enabled.
    drive_resistance
        Driver resistance used for computing elmore delay.
    delays : Dictionary of PvtCorner to IntristicDelay
        Delay through switch

    """

    def __init__(self, internal_capacitance, drive_resistance, delays):
        self.internal_capacitance = internal_capacitance
        self.drive_resistance = drive_resistance
        self.delays = delays

        self.downstream_cap = None
        self.rc_delay = None

    def set_sink_wire(self, wire):
        """ Sets sink wire for this output pin.

        An output pin always sinks to exactly 1 wire.

        This method must be called prior to calling propigate_delays method
        on the root Outpin object of this tree.

        Arguments
        ---------
        wire : Wire object
            Sink wire for this output pin.

        """
        self.sink_wire = wire

    def propigate_downstream_capacitance(self, math):
        assert self.sink_wire is not None
        self.downstream_cap = self.sink_wire.propigate_downstream_capacitance(
            math)
        return self.internal_capacitance

    def propigate_delays(self, elements, math):
        self.propigated_delays = list(elements)

        assert self.sink_wire is not None
        self.sink_wire.propigate_delays(self.propigated_delays + [self], math)
        self.rc_delay = math.multiply(
            self.downstream_cap, self.drive_resistance)

    def get_intrinsic_delays(self):
        return self.delays

    def get_rc_delay(self):
        assert self.rc_delay is not None
        return self.rc_delay

    def get_downstream_cap(self):
        assert self.downstream_cap is not None
        return self.downstream_cap


class PassTransistor(DownstreamNode):
    """ Represents a non-isolating switch.

    Arguments
    ---------
    drive_resistance
        Driver resistance used for computing elmore delay.
    delays : Dictionary of PvtCorner to IntristicDelay
        Delay through switch.

    """

    def __init__(self, drive_resistance, delays):
        self.drive_resistance = drive_resistance
        self.delays = delays
        self.sink_wire = None

        self.downstream_cap = None
        self.rc_delay = None

    def set_sink_wire(self, wire):
        """ Sets sink wire for this output pin.

        An output pin always sinks to exactly 1 wire.

        This method must be called prior to calling propigate_delays method
        on the root Outpin object of this tree.

        Arguments
        ---------
        wire : Wire object
            Sink wire for this output pin.

        """
        self.sink_wire = wire

    def propigate_downstream_capacitance(self, math):
        assert self.sink_wire is not None
        self.downstream_cap = self.sink_wire.propigate_downstream_capacitance(
            math)

        return self.downstream_cap

    def propigate_delays(self, elements, math):
        self.propigated_delays = list(elements)

        assert self.sink_wire is not None
        self.sink_wire.propigate_delays(self.propigated_delays + [self], math)
        self.rc_delay = math.multiply(
            self.downstream_cap, self.drive_resistance)

    def get_intrinsic_delays(self):
        return self.delays

    def get_rc_delay(self):
        assert self.rc_delay is not None
        return self.rc_delay

    def get_downstream_cap(self):
        assert self.downstream_cap is not None
        return self.downstream_cap
