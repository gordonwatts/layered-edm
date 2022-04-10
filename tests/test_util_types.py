import awkward as ak
import pytest
from layered_edm.util_types import append_awk_behavior_to_class, class_behavior


def test_class_behavior_none(ak_behavior):
    class my_test:
        pass

    assert class_behavior(my_test) is None


def test_class_behavior_add_one(ak_behavior):
    class my_test:
        pass

    class hi_there(ak.Array):
        def __init__(self):
            pass

    append_awk_behavior_to_class(my_test, hi_there, None)
    assert class_behavior(my_test) == "hi_there"


def test_class_behavior_add_two(ak_behavior):
    class my_test:
        pass

    class hi_there_1(ak.Array):
        def __init__(self):
            pass

    class hi_there_2(ak.Array):
        def __init__(self):
            pass

    append_awk_behavior_to_class(my_test, hi_there_1, None)
    append_awk_behavior_to_class(my_test, hi_there_2, None)
    r = class_behavior(my_test)

    assert r != "hi_there_1"
    assert r != "hi_there_2"


def test_class_behavior_add_two_with_registration(ak_behavior):
    class my_test:
        pass

    class hi_there_1(ak.Array):
        def __init__(self):
            pass

    class hi_there_2(ak.Array):
        def __init__(self):
            pass

    def reg_2():
        ak_behavior["hi_there_2"] = hi_there_2
        ak_behavior["*", "hi_there_2"] = hi_there_2

    append_awk_behavior_to_class(my_test, hi_there_1, None)
    append_awk_behavior_to_class(my_test, "hi_there_2", reg_2)
    r = class_behavior(my_test)

    assert r != "hi_there_1"
    assert r != "hi_there_2"


def test_class_behavior_callback(ak_behavior):
    class my_test:
        pass

    class hi_there(ak.Array):
        def __init__(self):
            pass

    seen = False

    def call_me():
        nonlocal seen
        seen = True

    append_awk_behavior_to_class(my_test, hi_there, call_me)
    class_behavior(my_test)

    assert seen


def test_class_behavior_unknown(ak_behavior):
    class my_test:
        pass

    append_awk_behavior_to_class(my_test, "hi_there", None)
    with pytest.raises(ValueError) as e:
        class_behavior(my_test)

    assert "hi_there" in str(e)
