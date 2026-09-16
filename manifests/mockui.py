# MockUI firmware manifest (hardware — STM32F469 Discovery)
include('../f469-disco/manifests/disco.py')
include('mockui-shared.py')
# The Schnuartz UI now shares Specter-DIY's storage crypto and JavaCard host
# modules. Freeze the complete application source so direct submodule imports
# keep the same package initialization behavior as the normal firmware.
freeze('../src')
# boot.py and main.py entry points
freeze('../scenarios/mockui_fw')
