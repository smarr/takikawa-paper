#!/usr/bin/env python3
from results import *

TODO = {
	"List-23": [17, 18], "Permute-14": 8,
	"CD-250": 107, 	"Richards-177": [172, 173], #24,
	"Snake-70": 61,  "Towers-30": 7,
	"DeltaBlue-243": [154, 155], "Go-230": [31, 47],
	"SpectralNorm-39": 27, "Json-134": 83}

res = []
i = 0
for bs, CA in TODO.items():
	CB = 0
	if isinstance(CA, list):
		CB = CA[1]
		CA = CA[0]

	b = benchmark(bs)
	r = RESULTS[b]		
	
	spoints0  = [((k.types/b.types)*100, v.times.m) for k, v in r.partial.items() if CA not in v.mask and CB not in v.mask]
	spointsA  = [((k.types/b.types)*100, v.times.m) for k, v in r.partial.items() if CA     in v.mask and CB not in v.mask]
	spointsB  = [((k.types/b.types)*100, v.times.m) for k, v in r.partial.items() if CA not in v.mask and CB     in v.mask]
	spointsAB = [((k.types/b.types)*100, v.times.m) for k, v in r.partial.items() if CA     in v.mask and CB     in v.mask]
	
	cpoints  = [(i - 0.5, v.m) for i, v in enumerate(r.single)]
	cpointA  = (CA - 0.5, r.single[CA].m)
	if CB != 0:
		cpointB  = (CB - 0.5, r.single[CB].m)

	ymax = max([y for _, y in spoints0 + spointsA + spointsB + spointsAB + cpoints])*1.1
	
	srel = ymax/r.partial[variant("0-0")].times.m
	crel = ymax/r.single[0].m

	tick_offset = floor_round(b.types/6, 5)

	sleft = f"Pattern = <{ymax}>, Scatter"
	if i % 2 == 0:
		sleft += ", Scatter Left Label"
	if len(TODO) - i <= 2:
		sleft += ", Scatter Bottom Label"
	sright = f"Pattern = <{srel}>, Scatter, Right Axis"
	
	cleft = f"Pattern = <{ymax}>, Column = <{tick_offset}>"	
	if len(TODO) - i <= 2:
		cleft += ", Column Bottom Label"
	cright = f"Pattern = <{crel}>, Column = <{tick_offset}>, Right Axis"
	if i % 2 == 1:
		cright += ", Column Right Label"

	res.append(double_axis(f"{sleft} = <{ymax}>", f"\\null\\hfill {b.name}", f"{sright} = <{srel}>", 
		plot("", *spoints0), plot("Pattern A", *spointsA), plot("Pattern B", *spointsB), plot("Pattern AB", *spointsAB)))

	columns = [plot("Pattern A", (CA - 0.5, 0), cpointA, (CA + 0.5, 0), (CA - 0.5, 0))]
	if CB != 0:
		columns += plot("Pattern B", (CB - 0.5, 0), cpointB, (CB + 0.5, 0), (CB - 0.5, 0))
		
	res.append(double_axis(f"{cleft} = <{ymax}><{floor_round(b.types/6, 5)}>", f"\\null\\hfill<\\small({b.types} Type Annotations)>", f"{cright} = <{crel}>", 
		plot("", *cpoints[1:], (len(r.single) - 0.5, 0), (0.5, 0)), *columns))
	
	i += 1
	
graphs(4, *res)
