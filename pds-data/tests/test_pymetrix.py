import unittest
from pds.pymetrix import calculate_metrics

class TestPymetrix(unittest.TestCase):
    
    def test_basic_metrics(self):
        code = """
def hello(name):
    # This is a comment
    print(f"Hello {name}")
    
def add(a, b):
    return a + b
"""
        metrics = calculate_metrics(code)
        self.assertEqual(metrics['NOF'], 2)
        self.assertEqual(metrics['LOC'], 5) # 2 defs + 1 comment + 2 code lines (ignoring only blanks)
        self.assertEqual(metrics['COM'], 1)
        self.assertEqual(metrics['BLK'], 2)

    def test_cyclomatic_complexity(self):
        code = """
def complex_func(x):
    if x > 0:
        if x < 10:
            return True
    elif x == 0:
        return False
    else:
        for i in range(10):
            print(i)
    return None
"""
        metrics = calculate_metrics(code)
        # 1 (base) + 1 (if) + 1 (if) + 1 (elif) + 1 (for) = 5
        self.assertEqual(metrics['CYC'], 5)

    def test_exception_metrics(self):
        code = """
try:
    raise ValueError("Error")
except ValueError:
    pass
finally:
    raise RuntimeError("Critical")
"""
        metrics = calculate_metrics(code)
        self.assertEqual(metrics['NER'], 2) # raise ValueError, raise RuntimeError
        self.assertEqual(metrics['NEH'], 1) # except ValueError

    def test_classes_and_methods(self):
        code = """
class MyClass:
    def method1(self):
        pass
    def method2(self, x):
        return x
"""
        metrics = calculate_metrics(code)
        self.assertEqual(metrics['NOC'], 1)
        self.assertEqual(metrics['AMC'], 2.0)
        self.assertEqual(metrics['APF'], 1.5) # (1 from method1 + 2 from method2) / 2 = 1.5

if __name__ == '__main__':
    unittest.main()
