# File: tests/test_rc.py

from dracklib.rc import RC


def test_rc_initialization():
    rc_instance = RC(ok=True, rc=200, msg="Success", obj={"key": "value"})
    assert rc_instance.ok is True
    assert rc_instance.rc == 200
    assert rc_instance.msg == "Success"
    assert rc_instance.obj == {"key": "value"}


def test_rc_ok_false():
    rc_instance = RC(ok=False, rc=404, msg="Not Found", obj=None)
    assert rc_instance.ok is False
    assert rc_instance.rc == 404
    assert rc_instance.msg == "Not Found"
    assert rc_instance.obj is None
