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
	left = "Full Scatter Left"
	if i == 18:
		left += " Corner"
	elif i == 19:
		left += " Bottom"
	elif i % 3 == 0:
		left += " Edge"
		
	right = "Full Scatter Right"
	if i % 3 == 2:
		right += " Edge"	
	
	res.append(double_axis(f"{left} = <{ymax}>", f"{b.name} <\\small({b.types} Type Annotations)>", f"{right} = <{yrelmax}>", 
			  plot("", *points)))
	
	i += 1
	
graphs(3, *res)
