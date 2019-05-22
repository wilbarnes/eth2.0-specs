import pytest

from eth2spec.phase0 import spec as built_phase0_spec
from eth2spec.phase1 import spec as built_phase1_spec

from preset_loader import loader

from tests.phase0 import helpers as phase0_helpers
from tests.phase1 import helpers as phase1_helpers


def pytest_addoption(parser):
    parser.addoption(
        "--config", action="store", default="minimal", help="config: make the pyspec use the specified configuration"
    )


@pytest.fixture(scope='session')
def phase0_spec(request):
    config_name = request.config.getoption("--config")

    presets = loader.load_presets('../../configs/', config_name, fork_name='phase0')
    built_phase0_spec.apply_constants_preset(presets)

    return built_phase0_spec


@pytest.fixture(scope='session')
def phase1_spec(request):
    config_name = request.config.getoption("--config")

    for fork_name in ('phase0', 'phase1'):
        presets = loader.load_presets('../../configs/', config_name, fork_name=fork_name)
        built_phase1_spec.apply_constants_preset(presets)

    return built_phase1_spec


@pytest.fixture(params=['phase0_spec', 'phase1_spec'], scope='session')
def spec(request, phase0_spec, phase1_spec):
    phase0_spec.id = 'phase0'
    phase1_spec.id = 'phase1'
    return {'phase0_spec': phase0_spec, 'phase1_spec': phase1_spec}[request.param]


@pytest.fixture
def num_validators(spec):
    return spec.SLOTS_PER_EPOCH * 8


@pytest.fixture
def deposit_data_leaves():
    return list()


@pytest.fixture
def state(num_validators, deposit_data_leaves, spec):
    return phase0_helpers.create_genesis_state(spec, num_validators, deposit_data_leaves)
