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
    parser.add_argument("-t", "--type",
                        choices=["reduce", "broadcast"],
                        help="the type of parallel run that is being done")
    args = parser.parse_args()
    return args

def build_intervals(lower_bound, upper_bound, step_size):
    """
    This function builds smaller intervals from the initial lower bound and upper bound.
    parameters:
    lower_bound: the lower bound of the definite integral
    upper_bound: the upper bound of the definite integral
    step_size: the number of steps to take in your numerical approximation
    returns: A list containing a tuple with the lower-, and upper bound along with the step size.
    """
    interval_size = (upper_bound - lower_bound) / size
    step_size = int(step_size / size)
    intervals = [(lower_bound + i * interval_size,
                  lower_bound + (i + 1) * interval_size, step_size) for i in range(size)]
    return intervals

def main():
    """
    Main function that dictates the flow of the program.
    In this case we let process with rank 0 build the intervals, and then we scatter them.
    After that we reduce and then print the final result once they're in.
    """
    arguments = argument_parsing()
    if arguments.step_size == 1:
        if rank == 0:
            result = trapezoid(cos, arguments.lower_bound, arguments.upper_bound, n=arguments.step_size)
            print(f"{arguments.step_size}:", result)
    else:
        if rank == 0:
            intervals = build_intervals(arguments.lower_bound, arguments.upper_bound, arguments.step_size)
        else:
            intervals = None
        local_interval = comm.scatter(intervals)
        local_lower_bound, local_upper_bound, local_n = local_interval
        local_result = trapezoid(cos, local_lower_bound,
                                 local_upper_bound, n=local_n)

        if arguments.type == "reduce":
            result = comm.reduce(local_result, op=MPI.SUM)
        else:
            result = comm.gather(local_result)
            if result is not None:
                result = sum(result)

        if rank == 0:
            print(f"{arguments.step_size}:", result)


if __name__ == "__main__":
    main()
