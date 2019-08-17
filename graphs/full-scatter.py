#!/usr/bin/env python3
from results import *

res = []
i = 0
for b, r in sorted(RESULTS.items(), key=lambda kv: kv[0].name):
	points = [((k.types/b.types)*100, v.times.m) for k, v in r.partial.items()]
	ymax = max([y for _, y in points])*1.1
	yrelmax = ymax/r.partial[variant("0-0")].times.m
	
	# This is a horrible way to manually get the left y axis labels only on the leftmost graphs,
	# and so on for the x axis, and right y axis.
	left = f"Full = <{ymax}>, Scatter"
	if i % 3 == 0:
		left += ", Scatter Left Label"
	if i >= 18:
		left += ", Scatter Bottom Label"
		
	right = f"Full = <{yrelmax}>, Scatter, Right Axis"
	if i % 3 == 2:
		right += ", Scatter Right Label"
	
	res.append(double_axis(left, f"{b.name} <\\small({b.types} Type Annotations)>", right,  plot("", *points)))
	
	i += 1
	
graphs(3, *res)
