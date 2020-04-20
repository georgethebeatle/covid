#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
ROOT_DIR="$SCRIPT_DIR/.."

pushd "$ROOT_DIR"
  kaggle datasets download sudalairajkumar/novel-corona-virus-2019-dataset
  tar -C data -xf novel-corona-virus-2019-dataset.zip covid_19_data.csv
  rm novel-corona-virus-2019-dataset.zip

  curl -sL -o data/population.csv https://raw.githubusercontent.com/datasets/population/master/data/population.csv
popd
