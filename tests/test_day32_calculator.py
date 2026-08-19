from app.tools.calculator import Calculator

def test_math():
    assert Calculator().calculate('25 * 6') == '150'
    assert Calculator().calculate('50 / 2') == '25'

def test_invalid():
    try: Calculator().calculate('invalid')
    except ValueError: pass
    else: assert False
