#!/usr/bin/env python3
import os
import sys
import trace

# for some reason unittest.main(module=None) kills the process
def inner_main():
    import runtests
    runtests.main()

def main():
    ignored = [
            sys.prefix,
            sys.exec_prefix,
            os.path.realpath('chintzy/tests/'),
    ]
    ignorem = [
            'coverage',
            'runtests',
    ]
    tracer = trace.Trace(
            ignoredirs=ignored, ignoremods=ignorem,
            trace=0, count=1)
    tracer.runfunc(inner_main)
    r = tracer.results()
    r.write_results(show_missing=True, coverdir='.coverage')

def main_maybe_pypy():
    try:
        import __pypy__
    except ImportError:
        print('Enabling coverage (running under CPython).')
        main()
    else:
        print('Disabling coverage (running under PyPy).')
        import runtests
        runtests.main()

if __name__ == '__main__':
    main_maybe_pypy()
