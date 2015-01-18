#!/usr/bin/env python3
import os
import sys
import trace

# For some reason, unittest.main(module=None) kills the process.
def inner_main():
    import runtests
    runtests.main()

def get_results():
    # The `trace` module has some major, documented, bugs in its
    # `ignoremods` facility, but `ignoredirs` seems to work.

    this_dir = os.path.realpath('chintzy/')

    ignored = [
            os.path.realpath('chintzy/tests/')
    ]
    for p in sys.path:
        p = os.path.realpath(p)
        if not this_dir.startswith(p):
            ignored.append(p)
    ignorem = [
            'coverage',
            'runtests',
    ]
    tracer = trace.Trace(
            ignoredirs=ignored, ignoremods=ignorem,
            trace=0, count=1)
    tracer.runfunc(inner_main)
    return tracer.results()

def main():
    r = get_results()
    # muck with undocumented internals
    old_counts = r.counts
    assert type(old_counts) == dict
    new_counts = {}
    all_standards = ['c89', 'c99', 'c11', 'cxx98', 'cxx11', 'cxx14']
    for ((f, l), c) in old_counts.items():
        for s in all_standards:
            f = f.replace('chintzy/%s/' % s, 'chintzy/c89/')
        c += new_counts.get((f, l), 0)
        new_counts[(f, l)] = c
    r.counts = new_counts
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
