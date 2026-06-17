#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_REPO="${UPSTREAM_REPO:-Fourgetu/3x-ui}"
UPSTREAM_REF="${UPSTREAM_REF:-main}"
RELEASE_REPO="${RELEASE_REPO:-${UPSTREAM_REPO}}"
TARGET_REPO="${TARGET_REPO:-${GITHUB_REPOSITORY:-}}"
TARGET_BRANCH="${TARGET_BRANCH:-${GITHUB_REF_NAME:-main}}"

if [[ -z "${TARGET_REPO}" ]]; then
    origin_url="$(git config --get remote.origin.url || true)"
    TARGET_REPO="$(printf '%s' "${origin_url}" | sed -E 's#^git@github.com:##; s#^https://github.com/##; s#\.git$##')"
fi

if [[ -z "${TARGET_REPO}" || "${TARGET_REPO}" == "${origin_url:-}" ]]; then
    echo "Unable to detect target GitHub repository. Set TARGET_REPO=owner/repo." >&2
    exit 1
fi

tmp_dir="$(mktemp -d)"
trap 'rm -rf "${tmp_dir}"' EXIT

raw_base="https://raw.githubusercontent.com/${UPSTREAM_REPO}/${UPSTREAM_REF}"
target_raw_base="https://raw.githubusercontent.com/${TARGET_REPO}/${TARGET_BRANCH}"

curl -fsSL "${raw_base}/install.sh" -o "${tmp_dir}/install.sh"
curl -fsSL "${raw_base}/x-ui.sh" -o "${tmp_dir}/x-ui.sh"

python3 scripts/translate-cn.py "${tmp_dir}/install.sh" install-cn.sh
python3 scripts/translate-cn.py "${tmp_dir}/x-ui.sh" x-ui-cn.sh

python3 scripts/translate-cn.py --patch-urls install-cn.sh \
    --upstream "${UPSTREAM_REPO}" \
    --upstream-ref "${UPSTREAM_REF}" \
    --release-repo "${RELEASE_REPO}" \
    --target-raw-base "${target_raw_base}"

python3 scripts/translate-cn.py --patch-urls x-ui-cn.sh \
    --upstream "${UPSTREAM_REPO}" \
    --upstream-ref "${UPSTREAM_REF}" \
    --release-repo "${RELEASE_REPO}" \
    --target-raw-base "${target_raw_base}"

curl -fsSL "https://api.github.com/repos/${RELEASE_REPO}/releases/latest" \
    | python3 -c 'import json,sys; data=json.load(sys.stdin); print(data["tag_name"])' \
    > upstream-version.txt

chmod +x install-cn.sh x-ui-cn.sh

echo "Synced ${UPSTREAM_REPO}@${UPSTREAM_REF} into ${TARGET_REPO}@${TARGET_BRANCH}"
echo "Upstream release: $(cat upstream-version.txt)"
