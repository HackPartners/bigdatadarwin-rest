import sys, os
sys.path.append(os.getcwd())

from common import util

def test_service():
    """Test whether the service() function returns the correct values."""

    tests = (
        ("0A43", util.TRAINID),
        ("4b54", util.TRAINID),
        ("L74238", util.UID),
        ("201509231033232", util.RID)
    )

    for test in tests:
        assert(test[1] == util.service(test[0]))
