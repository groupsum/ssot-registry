# Verification

Executed successfully:

- `python -m pip install -e .`
- `python -m unittest discover -s tests -v`
- `python -m compileall src tests`
- `python -m build`

Current test count: 13 passing tests.

Release-flow integration coverage includes:

- `ssot-registry init`
- `ssot-registry validate`
- `ssot-registry release certify`
- `ssot-registry release promote`
- `ssot-registry release publish`
- `ssot-registry graph export`
