run:
	poetry run scrap

shell:
	poetry run ipython

style:
	poetry run black .

test:
	poetry run pytest
