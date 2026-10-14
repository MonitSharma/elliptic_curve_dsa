# Source this file from bash or zsh: source ./activate.sh
if [ -n "${ZSH_VERSION:-}" ]; then
    _ecdsa_source="${(%):-%x}"
elif [ -n "${BASH_VERSION:-}" ]; then
    _ecdsa_source="${BASH_SOURCE[0]}"
else
    printf '%s\n' 'Please source activate.sh from bash or zsh.' >&2
    return 1
fi
_ecdsa_root="$(cd "$(dirname "$_ecdsa_source")" && pwd)"
. "$_ecdsa_root/.venv/bin/activate"
if [ -x "$_ecdsa_root/.tools/cargo/bin/rustup" ] && [ -d "$_ecdsa_root/.tools/rustup/toolchains" ]; then
    export CARGO_HOME="$_ecdsa_root/.tools/cargo"
    export RUSTUP_HOME="$_ecdsa_root/.tools/rustup"
    export PATH="$_ecdsa_root/.tools/cargo/bin:$PATH"
elif [ -f "$HOME/.cargo/env" ]; then
    . "$HOME/.cargo/env"
fi
export RUSTUP_TOOLCHAIN=1.93.0
export YUKON_CONFIG_DIR="$_ecdsa_root/.tools/config"
export CARGO_TARGET_DIR="$_ecdsa_root/target"
export PATH="$_ecdsa_root/.tools/bin:$PATH"
unset _ecdsa_source _ecdsa_root
