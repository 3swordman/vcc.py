python -m pip install build twine
mypy vcc_py
python -m build
twine upload dist/*