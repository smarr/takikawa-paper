#!/usr/bin/bash
# Updates the paper to make it suitable for positing to arxiv.org
T=$(mktemp)
latexmk # for bbl file
mkdir -p arxiv
cp acmart.cls arxiv/ # files we need
cp paper.bbl arxiv/ms.bbl

latexpand --empty-comments paper.tex --output arxiv/ms.tex
sed -i 's/]{acmart}/,authorversion=true]{acmart}\n\\pdfoutput=1\n\\settopmatter{printfolios=true}\n/' arxiv/ms.tex # Put appropriate copyright statement, force use of PDFLatex, and add page numbers

# Copy the pgfplots library (this is needed since arxiv.org has an out of date version)
find $(dirname $(kpsewhich pgfplots.sty)) -type f -exec cp {} arxiv/ \;
find $(dirname $(kpsewhich pgfplots.code.tex)) -type f -exec cp {} arxiv/ \;

# Now make the zip
cd arxiv
rm -f ../arxiv.zip &> /dev/null
zip ../arxiv.zip ./*
