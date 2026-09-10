# Top-level tests package shim.
# Re-export the tests from the cmms app so unittest discovery that imports
# a top-level `tests` package will find the cmms.tests package contents.
try:
    from cmms import tests as _cmms_tests

    # export public names from cmms.tests
    for _k, _v in _cmms_tests.__dict__.items():
        if not _k.startswith("_"):
            globals()[_k] = _v
except Exception:
    # If import fails, leave package empty; discovery will report errors normally.
    pass
