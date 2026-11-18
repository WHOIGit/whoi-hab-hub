#!/usr/bin/env bash
#
# upload_missing_bins.sh
#
# Recursively finds *.h5 files under a parent directory that contains one
# directory per model (named after the model ID), checks each Bin ID against
# the HABhub API, and uploads a file to S3 if either:
#   - the bin returns 404, or
#   - the file's model ID (= name of its model directory) is not in the
#     response's .properties.modelIds list.
#
# Usage:
#   ./upload_missing_bins.sh [-n] [-p aws_profile] <search_dir> <s3_bucket>
#
#   -n   Dry run: report what would be uploaded without uploading.
#   -p   AWS CLI profile name to use (from ~/.aws/config / credentials).
#        If omitted, the default credential chain is used.
#
# Example:
#   ./upload_missing_bins.sh -p wildharbor /data/ifcb my-bucket
#   /data/ifcb/model_id/D2026/D20260813T162616_IFCB236_class.h5
#     -> s3://my-bucket/wildharbor/v3-scan/model_id/D2026/D20260813T162616_IFCB236_class.h5
#
# The ingest Lambda reads the model ID from the third part of the S3 key, so the
# model directory has to be the first directory under <search_dir>. Files
# directly in <search_dir> aren't in a model directory and are skipped.
#
# Requires: curl, jq, aws CLI (configured with credentials for the bucket)

set -uo pipefail

API_BASE="https://habhub-api.whoi.edu/api/v2/ifcb-bins"
S3_PREFIX="wildharbor/v3-scan"

usage() {
    echo "Usage: $0 [-n] [-p aws_profile] <search_dir> <s3_bucket>" >&2
    exit 1
}

DRY_RUN=0
AWS_PROFILE_NAME=""
while getopts ":np:" opt; do
    case "$opt" in
        n) DRY_RUN=1 ;;
        p) AWS_PROFILE_NAME="$OPTARG" ;;
        *) usage ;;
    esac
done
shift $((OPTIND - 1))

[[ $# -ne 2 ]] && usage

AWS_ARGS=()
[[ -n "$AWS_PROFILE_NAME" ]] && AWS_ARGS+=(--profile "$AWS_PROFILE_NAME")

SEARCH_DIR="${1%/}"          # strip trailing slash
BUCKET="${2#s3://}"          # allow "s3://bucket" or "bucket"
BUCKET="${BUCKET%/}"

if [[ ! -d "$SEARCH_DIR" ]]; then
    echo "Error: '$SEARCH_DIR' is not a directory" >&2
    exit 1
fi

for cmd in curl aws jq; do
    command -v "$cmd" >/dev/null 2>&1 || { echo "Error: '$cmd' not found" >&2; exit 1; }
done

# Verify AWS credentials/profile up front (skipped on dry run)
if [[ $DRY_RUN -eq 0 ]]; then
    if ! aws "${AWS_ARGS[@]}" sts get-caller-identity >/dev/null 2>&1; then
        echo "Error: AWS credentials not valid${AWS_PROFILE_NAME:+ for profile '$AWS_PROFILE_NAME'}" >&2
        exit 1
    fi
fi

echo "Searching $SEARCH_DIR for model directories"

RESP_FILE="$(mktemp)"
trap 'rm -f "$RESP_FILE"' EXIT

checked=0; missing=0; nomodel=0; uploaded=0; failed=0; skipped=0

# upload_file <file> <bin_id> <reason: MISSING|NOMODEL>
# The S3 key is the file's path under the search directory, starting with the
# model directory, e.g. wildharbor/v3-scan/model_id/D2026/...
upload_file() {
    local file="$1" bin_id="$2" reason="$3"
    local rel_path="${file#"$SEARCH_DIR"/}"
    local s3_uri="s3://${BUCKET}/${S3_PREFIX}/${rel_path}"

    if [[ "$reason" == "MISSING" ]]; then ((missing++)); else ((nomodel++)); fi

    if [[ $DRY_RUN -eq 1 ]]; then
        echo "$reason $bin_id -> (dry run) $s3_uri"
    else
        echo "$reason $bin_id -> uploading to $s3_uri"
        if aws "${AWS_ARGS[@]}" s3 cp --only-show-errors "$file" "$s3_uri"; then
            ((uploaded++))
        else
            echo "ERROR  upload failed: $file" >&2
            ((failed++))
        fi
    fi
}

while IFS= read -r -d '' file; do
    filename="$(basename "$file")"

    # Model ID = name of the first directory under the search directory
    rel_path="${file#"$SEARCH_DIR"/}"
    if [[ "$rel_path" != */* ]]; then
        echo "SKIP   (not in a model directory) $file"
        ((skipped++))
        continue
    fi
    model_id="${rel_path%%/*}"

    # Extract Bin ID: e.g. D20260813T162616_IFCB236 from D20260813T162616_IFCB236_class.h5
    if [[ "$filename" =~ ^(D[0-9]{8}T[0-9]{6}_IFCB[0-9]+) ]]; then
        bin_id="${BASH_REMATCH[1]}"
    else
        echo "SKIP   (unrecognized name) $file"
        ((skipped++))
        continue
    fi

    ((checked++))
    status="$(curl -s -o "$RESP_FILE" -w '%{http_code}' --max-time 30 \
              --retry 3 --retry-delay 2 "${API_BASE}/${bin_id}/")"

    case "$status" in
        200)
            # Is model_id in .properties.modelIds? (missing/null list counts as "not present")
            jq -e --arg m "$model_id" \
                '(.properties.modelIds // []) | index($m) != null' \
                "$RESP_FILE" >/dev/null 2>&1
            jq_rc=$?
            if [[ $jq_rc -eq 0 ]]; then
                echo "EXISTS $bin_id (model '$model_id' present)"
            elif [[ $jq_rc -eq 1 ]]; then
                upload_file "$file" "$bin_id" "NOMODEL"
            else
                echo "WARN   $bin_id returned unparseable JSON (not uploaded)" >&2
                ((failed++))
            fi
            ;;
        404)
            upload_file "$file" "$bin_id" "MISSING"
            ;;
        *)
            echo "WARN   $bin_id returned HTTP $status (not uploaded)" >&2
            ((failed++))
            ;;
    esac
done < <(find "$SEARCH_DIR" -type f -name '*.h5' -print0)

echo
echo "Checked: $checked  Missing (404): $missing  Model not listed: $nomodel  Uploaded: $uploaded  Skipped: $skipped  Errors: $failed"
[[ $failed -eq 0 ]]
