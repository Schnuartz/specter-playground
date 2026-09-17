# MockUI firmware manifest (hardware — STM32F469 Discovery)
include('../f469-disco/manifests/disco.py')
# The hardware image has a much smaller executable flash region than the Unix
# and browser simulators.  Optimise the Python bytecode frozen into that region;
# the simulator manifests intentionally keep their normal debug-friendly level.
freeze('../scenarios/MockUI/src', opt=3)
# MockUI shares Specter-DIY's crypto helpers and JavaCard implementation.  Do
# not freeze the unrelated wallet application, legacy GUI and host trees into
# this dedicated firmware image.
freeze('../src', ('config_default.py', 'errors.py', 'helpers.py',
                  'platform.py', 'rng.py'), opt=3)
freeze('../src', ('keystore/__init__.py', 'keystore/core.py'), opt=3)
freeze('../src', 'keystore/javacard', opt=3)
# boot.py and main.py entry points
freeze('../scenarios/mockui_fw', opt=3)
