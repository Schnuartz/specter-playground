#!/usr/bin/env bash
set -euo pipefail

# Build the repository's real LVGL 9 MockUI application for the browser. The
# checked-out commit is the source of truth, so CI artifacts always match the
# commit that triggered the workflow.
WEB_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT_ROOT="$(cd "$WEB_ROOT/.." && pwd)"
PLAYGROUND_SRC="${PLAYGROUND_SRC:-$PROJECT_ROOT}"
EMSDK_ENV="${EMSDK_ENV:-$PROJECT_ROOT/.browser-work/emsdk/emsdk_env.sh}"
SOURCE_SHA="$(git -C "$PLAYGROUND_SRC" rev-parse HEAD)"
ORIGIN_URL="$(git -C "$PLAYGROUND_SRC" remote get-url origin)"
ORIGIN_REPOSITORY="$(printf '%s' "$ORIGIN_URL" | sed -E 's#^(https://github.com/|git@github.com:)##; s#\.git$##')"
SOURCE_REPOSITORY="${SPECTER_SOURCE_REPOSITORY:-${GITHUB_REPOSITORY:-$ORIGIN_REPOSITORY}}"
[[ "$SOURCE_REPOSITORY" =~ ^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$ ]] || { echo 'Invalid source repository' >&2; exit 1; }
OUT="$WEB_ROOT/builds/$SOURCE_REPOSITORY/$SOURCE_SHA"

if [[ "${SKIP_SUBMODULE_UPDATE:-0}" != 1 ]]; then
  git -C "$PLAYGROUND_SRC" submodule update --init bootloader f469-disco
fi
if [[ "${SKIP_SUBMODULE_UPDATE:-0}" != 1 ]] && [[ -e "$PLAYGROUND_SRC/f469-disco/.git" ]] && git -C "$PLAYGROUND_SRC/f469-disco" rev-parse --git-dir >/dev/null 2>&1; then
  git -C "$PLAYGROUND_SRC/f469-disco" submodule update --init \
    micropython usermods/secp256k1 usermods/udisplay_f469/lvgl
  git -C "$PLAYGROUND_SRC/f469-disco/micropython" submodule update --init \
    lib/axtls lib/mbedtls lib/micropython-lib
  git -C "$PLAYGROUND_SRC/f469-disco/usermods/secp256k1" submodule update --init secp256k1
else
  echo "Using populated f469-disco sources without a valid nested Git dir" >&2
fi

apply_if_needed() {
  local repo="$1" patch="$2"
  local top prefix
  top="$(git -C "$repo" rev-parse --show-toplevel)"
  if [[ "$top" = "$repo" ]]; then
    if git -C "$repo" apply --reverse --check "$patch" 2>/dev/null; then return; fi
    git -C "$repo" apply "$patch"
  else
    prefix="${repo#"$top"/}"
    [[ "$prefix" != "$repo" ]] || { echo "Patch path is outside Git root: $repo" >&2; exit 1; }
    if git -C "$top" apply --directory="$prefix" --reverse --check "$patch" 2>/dev/null; then return; fi
    git -C "$top" apply --directory="$prefix" "$patch"
  fi
}
apply_if_needed "$PLAYGROUND_SRC/f469-disco/micropython" "$WEB_ROOT/browser/v9-patches/micropython.patch"
if grep -q 'lv_sdl_mouse_handler(&event);' "$PLAYGROUND_SRC/f469-disco/usermods/udisplay_f469/lv_sdl_hal/SDL/modSDL.c"; then
  apply_if_needed "$PLAYGROUND_SRC/f469-disco" "$WEB_ROOT/browser/v9-patches/browser-pointer-events.patch"
fi
apply_if_needed "$PLAYGROUND_SRC/f469-disco" "$WEB_ROOT/browser/v9-patches/usermods.patch"
apply_if_needed "$PLAYGROUND_SRC/f469-disco/usermods/secp256k1" "$WEB_ROOT/browser/v9-patches/secp256k1.patch"
python3 "$WEB_ROOT/browser/patch-playground-qstr.py" "$PLAYGROUND_SRC/f469-disco/micropython"
python3 "$WEB_ROOT/browser/limit-lvgl.py" \
  "$PLAYGROUND_SRC/f469-disco/usermods/udisplay_f469/lvgl/lvgl.mk"

if ! command -v emcc >/dev/null; then
  test -f "$EMSDK_ENV" || { echo "Emscripten 3.1.74 is required" >&2; exit 1; }
  # shellcheck source=/dev/null
  source "$EMSDK_ENV" >/dev/null
fi
test "$(emcc --version | head -1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)" = 3.1.74 || {
  echo "Expected Emscripten 3.1.74" >&2
  exit 1
}

make -C "$PLAYGROUND_SRC" build-i18n
make -C "$PLAYGROUND_SRC" build-themes
python3 "$WEB_ROOT/browser/prepare-mockui.py" "$PLAYGROUND_SRC"
python3 "$WEB_ROOT/tests/test-browser-manifest.py" "$PLAYGROUND_SRC"
make -C "$PLAYGROUND_SRC/f469-disco/micropython/mpy-cross" -j4

PORT="$PLAYGROUND_SRC/f469-disco/micropython/ports/unix"
if [[ "${BROWSER_CLEAN:-1}" = 1 ]]; then
  make -C "$PORT" BUILD=build-specter-mockui-browser PROG=micropython.js clean
fi
make -C "$PORT" -j4 \
  BUILD=build-specter-mockui-browser PROG=micropython.js \
  CC=emcc LD=emcc AR=emar STRIP=true SIZE=true \
  MICROPY_PY_BTREE=0 MICROPY_PY_FFI=0 MICROPY_PY_SOCKET=0 \
  MICROPY_PY_THREAD=0 MICROPY_PY_TERMIOS=0 MICROPY_PY_USSL=0 \
  MICROPY_USE_READLINE=1 \
  USER_C_MODULES="$PLAYGROUND_SRC/f469-disco/usermods" \
  FROZEN_MANIFEST="$PLAYGROUND_SRC/browser.manifest.py" \
  CFLAGS_EXTRA="-DMICROPY_NLR_SETJMP=1 -DMICROPY_STACKLESS=1 -DMICROPY_STACKLESS_STRICT=1 -DMODULE_DISPLAY_ENABLED=1 -DMODULE_HASHLIB_ENABLED=1 -DMICROPY_PY_HASHLIB=0 -DSTATIC=static -Wno-error -sUSE_SDL=2 -ffile-prefix-map=$PLAYGROUND_SRC=/specter-playground" \
  LDFLAGS_ARCH= \
  LDFLAGS_EXTRA="-sUSE_SDL=2 -sASYNCIFY=1 -sASYNCIFY_STACK_SIZE=65536 -sALLOW_MEMORY_GROWTH=1 -sFORCE_FILESYSTEM=1 -sEXIT_RUNTIME=0 -sSTACK_SIZE=8388608 -sEXPORTED_RUNTIME_METHODS=FS,ccall --preload-file $WEB_ROOT/browser/runtime@/browser --preload-file $PLAYGROUND_SRC/build/flash_image@/flash -Wl,--allow-multiple-definition"

WASM_OPT="${WASM_OPT:-$(dirname "$(command -v emcc)")/../bin/wasm-opt}"
python3 "$WEB_ROOT/browser/optimize-wasm.py" \
  "$PORT/build-specter-mockui-browser/micropython.wasm" "$WASM_OPT"
python3 "$WEB_ROOT/browser/normalize-glue.py" \
  "$PORT/build-specter-mockui-browser/micropython.js"
mkdir -p "$OUT"
cp "$PORT/build-specter-mockui-browser"/micropython.{js,wasm,data} "$OUT/"
BROWSER_WASM_OPTIMIZED=1 python3 "$WEB_ROOT/browser/write-manifest.py" \
  "$PLAYGROUND_SRC" "$OUT" "$SOURCE_REPOSITORY" mockui
echo "MockUI browser artifacts: $OUT"
