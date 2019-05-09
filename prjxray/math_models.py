""" Math models are used to represent abstract operations for the timing models.
This is useful for creating excel workbooks that can update dynamically, or
generating a model with symbolic constants to be backsolved.
"""


class ExcelMathModel(object):
    """ Math model used for outputting to an dyanmic Excel sheet. """

    def __init__(self):
        pass

    def sum(self, elems):
        sum_val = '(' + ' + '.join(elems) + ')'
        if sum_val == '()':
            return '0'
        else:
            return sum_val

    def product(self, elems):
        sum_val = '(' + ' * '.join(elems) + ')'
        if sum_val == '()':
            return '1'
        else:
            return sum_val

    def plus(self, a, b):
        return self.sum((a, b))

    def divide(self, a, b):
        return '({}/{})'.format(a, b)

    def multiply(self, a, b):
        return '({}*{})'.format(a, b)

    def eval(self, elem):
        return '=' + elem


def PythonMathModel(object):
    """ Math model used for outputting values equalated immediately. """

    def __init__(self):
        pass

    def sum(self, elems):
        return sum(elems)

    def product(self, elems):
        v = 1.0
        for elem in elems:
            v *= elem
        return v

    def divide(self, a, b):
        return a / b

    def plus(self, a, b):
        return a + b

    def multiply(self, a, b):
        return a * b

    def eval(self, elem):
        return elem
