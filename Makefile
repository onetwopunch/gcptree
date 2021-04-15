clean:
	rm dist/*

deploy:
	python setup.py sdist && twine upload dist/*

test:
	pytest
