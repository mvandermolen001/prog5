import argparse
from math import cos

def trapezoid(f, a, b, *, n=1):
    """I = trapezoid(f, a, b, *, n=1).
    Calculates the definite integral of the function f(x)
    from a to b using the composite trapezoidal rule with
    n subdivisions (with default n=1).
    """
    h = (b - a) / n
    I = (f(a) + f(b) + 2 * sum(f(a+i*h) for i in range(1, n)))*(h/2)
    return I

def argument_parsing():
    """Parses command line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--lower_bound", help="the lower bound of the definite integral",
                        type=int)
    parser.add_argument("-b", "--upper_bound", help="the upper bound of the definite integral",
                        type=int)
    parser.add_argument("-n", "--step_size", help="the number of steps to take in your numerical approximation",
                        type=int)
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    arguments = argument_parsing()
    estimate = trapezoid(cos, arguments.lower_bound, arguments.upper_bound, n=arguments.step_size)
    print(arguments.step_size, estimate)