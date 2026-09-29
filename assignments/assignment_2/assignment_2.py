"""
Code for assignment two. This file contains the trapezoid function to numerically estimate a
definite integral of a function f(x). This estimation is done using openmpi's reduce method.
This means that the given interval gets split up into smaller intervals and then distributed.
The n, step_size, is divided by the amount of processes given. WARNING: this can give some errors
as it is expected that n is an integer when it is not, this function might be off.

For help, please use -h whilst calling the script.
"""

from mpi4py import MPI
import argparse
from math import cos

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

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
                        type=float)
    parser.add_argument("-b", "--upper_bound", help="the upper bound of the definite integral",
                        type=float)
    parser.add_argument("-n", "--step_size",
                        help="the number of steps to take in your numerical approximation",
                        type=int)
    args = parser.parse_args()
    return args

if rank == 0:
    arguments = argument_parsing()
    interval_size = (arguments.upper_bound - arguments.lower_bound) / size
    step_size = int(arguments.step_size / size)
    intervals = [(arguments.lower_bound + i * interval_size,
                  arguments.lower_bound + (i + 1) * interval_size, step_size) for i in range(size)]
else:
    intervals, arguments = None, None

local_interval = comm.scatter(intervals, root=0)
local_lower_bound, local_upper_bound, local_n = local_interval
local_result = trapezoid(cos,local_lower_bound,
    local_upper_bound,n=local_n)

result = comm.reduce(local_result, op=MPI.SUM, root=0)

if rank == 0:
    print(result)