from eth2spec.phase0 import spec as spec_phase0
from eth2spec.phase1 import spec as spec_phase1
from eth2spec.utils import bls

from .helpers.genesis import create_genesis_state

from .utils import spectest, with_tags


def with_state(fn):
    def entry(*args, **kw):
        try:
            kw['state'] = create_genesis_state(spec=kw['spec'], num_validators=spec_phase0.SLOTS_PER_EPOCH * 8)
        except KeyError:
            raise TypeError('Spec decorator must come before state decorator to inject spec into state.')
        return fn(*args, **kw)
    return entry


# BLS is turned off by default *for performance purposes during TESTING*.
# The runner of the test can indicate the preferred setting (test generators prefer BLS to be ON).
# - Some tests are marked as BLS-requiring, and ignore this setting.
#    (tests that express differences caused by BLS, e.g. invalid signatures being rejected)
# - Some other tests are marked as BLS-ignoring, and ignore this setting.
#    (tests that are heavily performance impacted / require unsigned state transitions)
# - Most tests respect the BLS setting.
DEFAULT_BLS_ACTIVE = False


# shorthand for decorating @with_state @spectest()
def spec_state_test(fn):
    return with_state(bls_switch(spectest()(fn)))


def expect_assertion_error(fn):
    bad = False
    try:
        fn()
        bad = True
    except AssertionError:
        pass
    except IndexError:
        # Index errors are special; the spec is not explicit on bound checking, an IndexError is like a failed assert.
        pass
    if bad:
        raise AssertionError('expected an assertion error, but got none.')


# Tags a test to be ignoring BLS for it to pass.
bls_ignored = with_tags({'bls_setting': 2})


def never_bls(fn):
    """
    Decorator to apply on ``bls_switch`` decorator to force BLS de-activation. Useful to mark tests as BLS-ignorant.
    """
    def entry(*args, **kw):
        # override bls setting
        kw['bls_active'] = False
        return fn(*args, **kw)
    return bls_ignored(entry)


# Tags a test to be requiring BLS for it to pass.
bls_required = with_tags({'bls_setting': 1})


def always_bls(fn):
    """
    Decorator to apply on ``bls_switch`` decorator to force BLS activation. Useful to mark tests as BLS-dependent.
    """
    def entry(*args, **kw):
        # override bls setting
        kw['bls_active'] = True
        return fn(*args, **kw)
    return bls_required(entry)


def bls_switch(fn):
    """
    Decorator to make a function execute with BLS ON, or BLS off.
    Based on an optional bool argument ``bls_active``, passed to the function at runtime.
    """
    def entry(*args, **kw):
        old_state = bls.bls_active
        bls.bls_active = kw.pop('bls_active', DEFAULT_BLS_ACTIVE)
        out = fn(*args, **kw)
        bls.bls_active = old_state
        return out
    return entry


def with_phase0(fn):
    """
    Decorator to use phase 0's spec and helpers
    """
    def entry(*args, **kw):
        kw['spec'] = spec_phase0
        return fn(*args, **kw)
    return entry


def with_phase1(fn):
    """
    Decorator to use phase 1's spec and helpers
    """
    def entry(*args, **kw):
        kw['spec'] = spec_phase1
        return fn(*args, **kw)
    return entry


def with_all_phases(fn):
    """
    Decorator to run everything with all availible spec phases
    """
    def entry(*args, **kw):
        kw['spec'] = spec_phase0
        fn(*args, **kw)
        kw['spec'] = spec_phase1
        return fn(*args, **kw)
    return entry
