# MockUI firmware manifest (hardware — STM32F469 Discovery)
include('../f469-disco/manifests/disco.py')
include('mockui-shared.py')
# The Schnuartz UI now shares Specter-DIY's storage crypto and JavaCard host
# modules. Freeze the application source except its normal ``main.py`` entry;
# this manifest supplies the MockUI entry point below.
freeze('../src', ('app.py', 'config_default.py', 'errors.py', 'helpers.py',
                  'platform.py', 'qrencoder.py', 'rng.py', 'specter.py'))
freeze('../src', 'apps')
freeze('../src', 'gui')
freeze('../src', 'hosts')
freeze('../src', 'keystore')
# boot.py and main.py entry points
freeze('../scenarios/mockui_fw')
