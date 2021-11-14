import friendly_traceback


def test_Not_enough_values_to_unpack():
    d = (1,)
    try:
        a, b, *c = d
    except ValueError:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    
    assert (
        "ValueError: not enough values to unpack (expected at least 2, got 1)" in result
    )
    if friendly_traceback.get_lang() == "en":
        assert "a `tuple` of length 1" in result

    try:
        for x, y, z in enumerate(range(3)):
            pass
    except ValueError:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert "ValueError: not enough values to unpack (expected 3, got 2)" in result

    d = "ab"
    try:
        a, b, c = d
    except ValueError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    
    assert "ValueError: not enough values to unpack (expected 3, got 2)" in result
    if friendly_traceback.get_lang() == "en":
        assert "a string (`str`) of length 2" in result
    return result, message


def test_Too_many_values_to_unpack():
    c = [1, 2, 3]
    try:
        a, b = c
    except ValueError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    
    assert "ValueError: too many values to unpack (expected 2)" in result
    if friendly_traceback.get_lang() == "en":
        assert "a `list` of length 3" in result
    return result, message


def test_Date_invalid_month():
    from datetime import date
    try:
        d = date(2021, 13, 1)
    except ValueError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "month must be in 1..12" in result
    if friendly_traceback.get_lang() == "en":
        assert "Valid values are integers, from 1 to 12" in result
    return result, message


def test_slots_conflicts_with_class_variable():
    try:
        class F:
            __slots__ = ["a", "b"]
            a = 1
    except ValueError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    assert "'a' in __slots__ conflicts with class variable" in result
    if friendly_traceback.get_lang() == "en":
        assert "is used both as the name of a class variable" in result
    return result, message


def test_time_strptime_incorrect_format():
    import time
    try:
        time.strptime("2020-01-01", "%d %m %Y")
    except ValueError as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert "time data '2020-01-01' does not match format '%d %m %Y'" in result
    if friendly_traceback.get_lang() == "en":
        assert "The value you gave for the time is not in the format you specified." in result

    return result, message



if __name__ == "__main__":
    print(test_Too_many_values_to_unpack()[0])
