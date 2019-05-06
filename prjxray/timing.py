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

1. Out-pins
2. Buffer switches
3. Pass-through switches
4. Wires
5. In-pins

Outpins have intristic delays and an driver resistence.

Buffer switches have instrinsic delays, internal capacitance, and output driver
resistence.

Pass-through switches have instrinsic delays and a resistence and capacitance.

Wires have a resistence and capacitance.

Inpins have instrinsic delays and a sink capacitance.

The elmore delay is the RC tree formed by these 5 components.  Out pins and
buffer switches are the roots of the elmore tree. Buffer switches
and inpins are leafs of the elmore tree. Wires and pass-through switches are
nodes in the tree, and share their capacitance upstream and downstream using a
pi-model.

"""
import enum
from collections import namedtuple

class PvtCorner(enum.Enum):
    """ Process/voltage/temperature corner definitions. """

    # Corner where device operates with fastest intristic delays.
    FAST = "FAST"

    # Corner where device operates with slowest intristic delays.
    SLOW = "SLOW"

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

    max : str
        Maximum instrinsic delay (nsec)
    """

class RcElement(namedtuple('RcElement', 'resistence capacitance')):
    """ One part of an RcNode, embedded within an RcTree.

    """
    pass


def fast_slow_tuple_to_corners(arr):
    """ Convert delay 4-tuple into two IntristicDelay objects.

    Returns
    -------

    corners : dict of PvtCorner to IntristicDelay
        Dictionary keys of FAST and SLOW, mapping to the instrinsic delay
        for each corner.

    """

    fast_min, fast_max, slow_min, slow_max = map(float, arr)

    return {
            PvtCorner.FAST: IntristicDelay(
                min=fast_min,
                max=fast_max,
                ),
            PvtCorner.SLOW: IntristicDelay(
                min=slow_min,
                max=slow_max,
                ),
            }
