.PHONY: test lint package

test:
	python -m unittest discover -s tests -v

lint:
	python -m compileall src tests

package:
	python -m pip install --upgrade build
	python -m build
