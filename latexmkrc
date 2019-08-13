@default_files = ("paper.tex");
$pdf_mode = 1; # Use pdflatex
$bibtex_use = 2; # Run bibtex/biber when necessary, delete .bbl on cleanup 
push @extra_pdflatex_options, "--interaction=errorstopmode";
#push @generated_exts, 'vtc'; # Tell latexmk that these files are generated
