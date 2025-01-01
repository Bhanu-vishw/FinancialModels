import pytest

from final import blackscholes as bs

def test_itm_call():
    call = True
    args = {
        "s": 75.5,
        "k": 50.25,
        "r": 0.10,
        "q": 0.02,
        "v": 0.35,
        "t": 2.5,
    }
    assert bs.price(**args, is_call=call) == pytest.approx(34.6578940888037)
    assert bs.delta(**args, is_call=call) == pytest.approx(0.870607763233823)
    assert bs.gamma(**args) == pytest.approx(0.00353504880571565)
    assert bs.vega(**args) == pytest.approx(0.176318292104331 * 100)
    assert bs.theta(**args, is_call=call) == pytest.approx(-0.0082929028103623 * 365)


def test_otm_call():
    call = True
    args = {
        "s": 35.4,
        "k": 55.25,
        "r": 0.08,
        "q": 0.04,
        "v": 0.25,
        "t": 1.5,
    }
    assert bs.price(**args, is_call=call) == pytest.approx(0.61084957151139)
    assert bs.delta(**args, is_call=call) == pytest.approx(0.126778632636872)
    assert bs.gamma(**args) == pytest.approx(0.0188280918577903)
    assert bs.vega(**args) == pytest.approx(0.0884797934719067 * 100)
    assert bs.theta(**args, is_call=call) == pytest.approx(-0.00237803339824326 * 365)


def test_itm_put():
    call = False
    args = {
        "s": 40.15,
        "k": 65.25,
        "r": 0.08,
        "q": 0.03,
        "v": 0.25,
        "t": 2.33,
    }
    assert bs.price(**args, is_call=call) == pytest.approx(18.2202245870577)
    assert bs.delta(**args, is_call=call) == pytest.approx(-0.728506968428777)
    assert bs.gamma(**args) == pytest.approx(0.0179615806241197)
    assert bs.vega(**args) == pytest.approx(0.168659799992082 * 100)
    assert bs.theta(**args, is_call=call) == pytest.approx(0.00552128343262734 * 365)


def test_otm_put():
    call = False
    args = {
        "s": 55.5,
        "k": 45.5,
        "r": 0.06,
        "q": 0.02,
        "v": 0.40,
        "t": 1.75,
    }
    assert bs.price(**args, is_call=call) == pytest.approx(4.75915233585737)
    assert bs.delta(**args, is_call=call) == pytest.approx(-0.212398368063912)
    assert bs.gamma(**args) == pytest.approx(0.00973454908377432)
    assert bs.vega(**args) == pytest.approx(0.209893913707071 * 100)
    assert bs.theta(**args, is_call=call) == pytest.approx(-0.00449784676156258 * 365)
