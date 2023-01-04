#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset

curl -sf --proto =https --tlsv1.2 https://botsin.space/api/v1/statuses -H "Authorization: Bearer $MASTODON_TOKEN" -d "visibility=unlisted" -d "status=Changes to Bundesrecht"
