
install: csurf.so
	cp csurf.so ../

build : csurf.so

csurf.so: csurf.pyx
	python setup.py build_ext --inplace

