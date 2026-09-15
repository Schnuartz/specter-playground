# Specter-Playground

    "Cypherpunks write code. We know that someone has to write software to defend privacy, 
    and since we can't get privacy unless we all do, we're going to write it."
    A Cypherpunk's Manifesto - Eric Hughes - 9 March 1993

    ...and Cypherpunks do build their own Bitcoin Hardware Wallets.

![](./docs/pictures/kit.jpg)

The idea of the project is to provide a playground for everyone to play with a software which can potentially run on the Specter Hardware, a F469-Discovery board from STMicroelectronics.

## setup
```
# in an empty dir
git clone https://github.com/cryptoadvance/specter-diy.git
cd specter-diy
git fetch origin pull/304/head:pr-304
git checkout pr-304
git submodule sync --recursive
git submodule update --init --recursive --checkout
make unix
./bin/micropython_unix f469-disco/usermods/udisplay_f469/udisplay_demo.py
```

```
# install nix
# install direnv
direnv allow
make unix
make simulate
# hack on address_navigator.py
```

## Scenarios

Different UI scenarios can be tested using the `SCRIPT` parameter:

```bash
# Default - runs mock_structure.py (main navigation menu)
nix develop -c make simulate SCRIPT=mock_structure.py

# Run address_navigator scenario
nix develop -c make simulate SCRIPT=address_navigator.py

# Run udisplay_demo scenario
nix develop -c make simulate SCRIPT=udisplay_demo.py
```

### Mock Structure
![](./docs/mock_structure.png)

### Address Navigator
![](./docs/address_simulator.png)

### UDisplay Demo
![](./docs/udisplay_demo.png)

## Schnuartz UI variant

The MockUI firmware uses the Schnuartz 480×800 layout and navigation while
keeping the playground's hardware-tested controller, build manifests and
binary settings architecture. The permanent frame is a 56 px top bar and a
56 px bottom navigation bar; the dashboard and all feature pages live in the
remaining viewport.

Colors and fonts are resolved through the active theme. The reference palette
is stored in
`scenarios/MockUI/src/MockUI/basic/theming/themes/specter_ui_theme_specter.json`.
User-facing strings are stored in
`scenarios/MockUI/src/MockUI/basic/i18n/languages/`.

To include German and an additional bundled theme in a build:

```bash
make unix ADD_LANG=de ADD_THEME=specter2
make mockui ADD_LANG=de ADD_THEME=specter2
```

Runtime imports use the same JSON formats as the build tools. Copy language
files named `specter_ui_<code>.json` or theme files named
`specter_ui_theme_<name>.json` to the root of the SD card. Enable/detect the SD
card, then use Settings → Language/Theme → Load from SD Card. Imports are
compiled and validated before the previous binary is replaced; incompatible
language key tables and incomplete theme triples are ignored on startup.
