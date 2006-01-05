all: doc

doc:
	#rest2latex README > README.latex 
	rest2latex --use-latex-toc --use-latex-docinfo --language=fr README > README.latex
	patch < README.latex.patch
	pdflatex README.latex 
	pdflatex README.latex 
	@echo "\nREADME.pdf is done\n"

clean:
	@find ./ -name "*.log" -exec rm -f {} \;
	@find ./ -name "*.out" -exec rm -f {} \;
	@find ./ -name "*.aux" -exec rm -f {} \;
	@rm -f *.bak
	@rm -f *.latex
	@rm -f *.toc

