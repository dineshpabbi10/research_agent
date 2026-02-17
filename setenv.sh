
#!/usr/bin/env bash
# set_env.sh - intended to be *sourced* to export env vars for the project

# Detect whether the script is being sourced
_is_sourced() {
	# ${BASH_SOURCE[0]} != $0 when sourced
	[ "${BASH_SOURCE[0]}" != "${0}" ]
}

if ! _is_sourced; then
	cat <<'MSG'
This script must be sourced to export environment variables into your shell.
Usage:
	source ./set_env.sh
or
	. ./set_env.sh
MSG
	exit 1
fi

# Project root: parent of this script's directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/" && pwd)"

echo "Sourcing environment variables from ${SCRIPT_DIR}/set_env.sh..."
echo "Assuming project root is ${PROJECT_ROOT}..."

# Common env vars (override by exporting before sourcing or via .env)
: "${PROJECT_ROOT}" >/dev/null
export PROJECT_ROOT

export LANGGRAPH_DATA_DIR="${PROJECT_ROOT}/data"
export LANGGRAPH_VENV_DIR="${PROJECT_ROOT}/.venv"

# Optionally load a .env file if present in project root
if [ -f "${PROJECT_ROOT}/.env" ]; then
	# export all KEY=VALUE pairs from .env
	set -o allexport
	# shellcheck disable=SC1090
	source "${PROJECT_ROOT}/.env"
	set +o allexport
fi

# If a virtualenv exists, optionally activate it
if [ -f "${LANGGRAPH_VENV_DIR}/bin/activate" ]; then
	# Don't auto-activate; just provide a convenient helper
	export LANGGRAPH_VENV_ACTIVATE="source \"${LANGGRAPH_VENV_DIR}/bin/activate\""
else
	unset LANGGRAPH_VENV_ACTIVATE 2>/dev/null || true
fi

# Helpful summary
echo "Exported: PROJECT_ROOT=${PROJECT_ROOT}"
echo "Exported: LANGGRAPH_DATA_DIR=${LANGGRAPH_DATA_DIR}"
echo "Exported: LANGGRAPH_VENV_DIR=${LANGGRAPH_VENV_DIR}"
if [ -n "${LANGGRAPH_VENV_ACTIVATE}" ]; then
	echo "Activate venv: ${LANGGRAPH_VENV_ACTIVATE}"
fi

return 0

