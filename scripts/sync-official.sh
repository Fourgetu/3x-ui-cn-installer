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

github_raw_api_url() {
    local url="$1" path owner repo ref
    case "$url" in
        https://raw.githubusercontent.com/*) ;;
        *) return 1 ;;
    esac

    path="${url#https://raw.githubusercontent.com/}"
    owner="${path%%/*}"
    path="${path#*/}"
    repo="${path%%/*}"
    path="${path#*/}"
    ref="${path%%/*}"
    path="${path#*/}"

    [[ -n "$owner" && -n "$repo" && -n "$ref" && -n "$path" ]] || return 1
    printf 'https://api.github.com/repos/%s/%s/contents/%s?ref=%s\n' "$owner" "$repo" "$path" "$ref"
}

download_github_file() {
    local output="$1" url="$2" api_url tmp
    tmp="${output}.tmp.$$"

    if curl -fsSL --retry 5 --retry-delay 3 --connect-timeout 15 --max-time 120 -o "$tmp" "$url"; then
        mv -f "$tmp" "$output"
        return 0
    fi

    rm -f "$tmp"
    api_url="$(github_raw_api_url "$url")" || return 1

    if curl -fsSL --retry 5 --retry-delay 3 --connect-timeout 15 --max-time 120 \
        -H 'Accept: application/vnd.github.raw' -o "$tmp" "$api_url"; then
        mv -f "$tmp" "$output"
        return 0
    fi

    rm -f "$tmp"
    return 1
}

download_github_file "${tmp_dir}/install.sh" "${raw_base}/install.sh"
download_github_file "${tmp_dir}/x-ui.sh" "${raw_base}/x-ui.sh"

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
