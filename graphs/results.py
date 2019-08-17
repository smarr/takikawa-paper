#!/usr/bin/env python3
import sys
from collections import defaultdict
from statistics import mean, stdev, median
from scipy.stats import norm
from math import sqrt
import pickle

# Some variables
W = 350 # Number of warmup iterations to skip
Z = norm.ppf((1+0.95)/2) # Z score, representing a 95% confidence interval

PICKLE_FILE = "results.pickle"
DATA_FILE = "results.data"
TYPEMASK_FILE = "results.typemasks"

# Some usefull functions
def eprint(*args, **kwargs):
	print(*args, file=sys.stderr, **kwargs)
def log(a, b): # For debuging, prints a, and then returns the result of evaluating b
	eprint(a)
	return b()
def printl(arg): # Converts < to { and > to }, so that format strings don't get horrible messy with tons of doubled {{ and }}
	print(arg.replace("<", "{").replace(">", "}"))

class defaultlist(list): # Stolen from https://stackoverflow.com/questions/8749542/creating-a-defaultlist-in-python
    def __init__(self, fx):
        self._fx = fx
    def _fill(self, index):
        while len(self) <= index:
            self.append(self._fx())
    def __setitem__(self, index, value):
        self._fill(index)
        list.__setitem__(self, index, value)
    def __getitem__(self, index):
        self._fill(index)
        return list.__getitem__(self, index)

# A class to handle interval arrithmetic, Interval(l, m, u) represents a closed interval between l and u, whith m as specific point inbetween
# (the idea is that "m" represents an approximate value, and l and u represent lower/upper limits of the value)
class Interval:
	def __init__(self, l, m=None, u=None, data=None):		
		if (m == None): 
			m = l
			u = l;
		self.l = l; self.m = m; self.u = u; self.data = data

	def convert(other):
		return other if isinstance(other, Interval) else Interval(other);
	def width(self):
		#assert self.midpoint = self.m
		return self.u - self.l
	def midpoint(self):
		return (self.u + self.l) / 2
	def __str__(self):
		return f"[{self.l}, {self.m}, {self.u}]"
	
	def __add__(self, other):
		other = Interval.convert(other)
		return Interval(self.l + other.l, self.m + other.m, self.u + other.u)
	def __sub__(self, other):
		other = Interval.convert(other)
		return Interval(self.l - other.l, self.m - other.m, self.u - other.u)

	def __mul__(self, other):
		other = Interval.convert(other)
		factors = [self.l * other.l, self.l * other.u, self.u * other.l, self.u * other.u ]
		return Interval(min(factors), self.m * other.m, max(factors))
	def __truediv__(self, other):
		other = Interval.convert(other)
		return self*Interval(1/other.u, 1/other.m, 1/other.l)

	def __radd__(self, other):
		return Interval.convert(other) + self
	def __rsub__(self, other):
		return Interval.convert(other) - self
	def __rmul__(self, other):
		return Interval.convert(other) * self
	def __rtruediv__(self, other):
		return Interval.convert(other) / self
	

def sumarise(ys0): # Returns the confidence interval for the mean of ys (skipping warmup of course)
	ys = ys0[W:]
	m = mean(ys)
	e = Z*(stdev(ys, m)/sqrt(len(ys)))
	return Interval(m-e, m, m+e, ys0) # return the range the mean might fall into

# Prints a graph
def axis(style, title, *plots):
	plots = "".join(plots)
	return f"\\AXIS<{style}, title=<{title}><\n{plots}>"

# Prints a graph with a second axis
def double_axis(style, title, second_style, *plots):
	plots = "".join(plots)
	return f"\\DOUBLEAXIS<{style}, title=<{title}>><{second_style}><\n{plots}>"
	
def graphs(columns, *axes):
	res = ""
	for i, a in enumerate(axes):
		if i % columns == 0 and i > 0:
			res += "\n\\\\\n"
		elif i % columns != 0:
			res += "\n\\&\n"
		res += a
	printl(f"\\GRAPHS<\n{res}\n>")

# Return a "plot" (a line, a set of points, a bunch of columns, etc.)
def plot(options, *points): # each point should be a pair (x, y) or (x, Interval(error-, y, error+))
	res = f"\t\\addplot+[{options}] coordinates<\n"
	for x, i in points: # i should be an interval
		if (isinstance(i, Interval)):
			res += f"\t\t({x}, {i.m})\n "#+- ({i.u - i.m}, {i.m - i.l})\n"
		else:
			res += f"\t\t({x}, {i})\n"

	return res + f"\t>;\n\n"

# Get the points of a rectangle...
def rectangle(x, width, y, height):
	return [(x, y), (x, y + height), (x + width, y + height), (x + width, y), (x, y)]

# A very inefficient dynamic struct type,
# just use "S(f1 = v1, ..., fn = vn)" to create one, and myS.f, myS.f = v to get and update/initilise fields
# comes with free ==, hash, repr, and str methods
class S:
	def __init__(self, **d):
		for k, v in d.items():
			self.__dict__[k] = v
	def __eq__(self, other):
		return self.__dict__ == other.__dict__
	def __hash__(self):
		return hash(tuple(sorted(self.__dict__.items()))) # To get a stable hash
	def __repr__(self):
		return repr(self.__dict__)

def benchmark(s):
	bn = s.split("-")
	return S(name = bn[0], types = int(bn[1]))
def variant(s):
	vn = s.split("-")
	return S(index = int(vn[0]), types = int(vn[1]))

def floor_round(num, base):
	return max(5, int(num//base)*base)

# Have to use functions (and not lambdas) so they can be pickled
def empty_result():
	return S(partial = defaultdict(empty_partial_result), single = defaultlist(list))
def empty_partial_result():
	return S(times = list(), mask = list())

# Now will load the "RESULTS" table, either from a cache or by converting the raw data
# The format of the table will be:
#	S(name=str, types=int) -> S(partial = S(index=int, types=int) -> S(times = Interval, mask = [int]), single = [Interval])
# (where -> indicates a dictionary)
RESULTS = None

try:
	with open(PICKLE_FILE, "rb") as f:
		RESULTS = pickle.load(f)

except IOError: # pickle file did not exist, so read the data in
	RESULTS = defaultdict(empty_result)
	for line in open(DATA_FILE):
		if line.startswith("#"):
			continue
		line = line.split("\t")
		r = RESULTS[benchmark(line[5])]
		if line[7] == "partial-type-cost":
			r.partial[variant(line[10])].times.append(float(line[2]))
		else:
			assert line[7] == "single-type-cost"
			r.single[int(line[10])].append(float(line[2]))
	# Now sumarise all the results (so I don't have to keep recomputing them!)
	for r in RESULTS.values():
		for pr in r.partial.values():
			pr.times = sumarise(pr.times)
		r.single = [sumarise(sr) for sr in r.single]
	
	for line in open(TYPEMASK_FILE):
		if line.startswith("#"):
			continue
		line = line.split("\t")
		RESULTS[benchmark(line[0])].partial[variant(line[1])].mask = [i + 1 for i, m in enumerate(line[2]) if m == '+']

	pickle.dump(RESULTS, open(PICKLE_FILE, "wb"))
