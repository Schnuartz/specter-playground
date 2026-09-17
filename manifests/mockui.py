# MockUI firmware manifest (hardware — STM32F469 Discovery)
include('../f469-disco/manifests/disco.py')
# The hardware image has a much smaller executable flash region than the Unix
# and browser simulators.  Optimise the Python bytecode frozen into that region;
# the simulator manifests intentionally keep their normal debug-friendly level.
freeze('../scenarios/MockUI/src', opt=3)
# The Schnuartz UI now shares Specter-DIY's storage crypto and JavaCard host
# modules. Freeze the application source except its normal ``main.py`` entry;
# this manifest supplies the MockUI entry point below.
freeze('../src', ('app.py', 'config_default.py', 'errors.py', 'helpers.py',
                  'platform.py', 'qrencoder.py', 'rng.py', 'specter.py'), opt=3)
freeze('../src', 'apps', opt=3)
freeze('../src', 'gui', opt=3)
freeze('../src', 'hosts', opt=3)
freeze('../src', 'keystore', opt=3)
# boot.py and main.py entry points
freeze('../scenarios/mockui_fw', opt=3)
