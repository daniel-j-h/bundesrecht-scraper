#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset

curl -sSf --proto =https --tlsv1.3 https://www.gesetze-im-internet.de/gii-toc.xml | xmllint --format - > gii-toc.xml
