from contextlib import contextmanager
import unittest

from appmap._implementation import testing_framework
import appmap.wrapt as wrapt


session = testing_framework.session('unittest')

def get_test_location(cls, method_name):
    from appmap._implementation.utils import get_function_location
    fn = getattr(cls, method_name)
    return get_function_location(fn)


# unittest.case._Outcom.testPartExecutor is used by all supported
# versions of unittest to run test cases. `isTest` will be True when
# the part is the actual test method, False when it's setUp or
# teardown.
@wrapt.patch_function_wrapper('unittest.case', '_Outcome.testPartExecutor')
@contextmanager
def testPartExecutor(wrapped, _, args, kwargs):
    def _args(test_case, *_, isTest=False, **__):
        return (test_case, isTest)
    test_case, is_test = _args(*args, **kwargs)
    if not is_test:
        with wrapped(*args, **kwargs):
            yield
        return

    method_name = test_case.id().split('.')[-1]
    location = get_test_location(test_case.__class__, method_name)
    with session.record(
            test_case.__class__,
            method_name,
            location=location):
        with wrapped(*args, **kwargs):
            yield

if __name__ == '__main__':
    unittest.main(module=None)
