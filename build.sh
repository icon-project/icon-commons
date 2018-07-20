#!/bin/bash
set -e

PYVER=$(python -c 'import sys; print(sys.version_info[0])')
if [[ PYVER -ne 3 ]];then
  echo "The script should be run on python3"
  exit 1
fi

if [[ ("$1" = "test" && "$2" != "--ignore-test") || ("$1" = "build") || ("$1" = "deploy") ]]; then
  pip install -r requirements.txt

  if [[ "$2" != "--ignore-test" ]]; then
    python -m unittest
  fi

  if [ "$1" = "build" ] || [ "$1" = "deploy" ]; then
    pip install wheel
    rm -rf build dist *.egg-info
    python setup.py bdist_wheel

    if [ "$1" = "deploy" ]; then
      VER=$(cat VERSION)

      if [[ -z "${AWS_ACCESS_KEY_ID}" || -z "${AWS_SECRET_ACCESS_KEY}" ]]; then
        echo "Error: AWS keys should be in your environment"
        exit 1
      fi

      pip install awscli
      aws s3 cp VERSION s3://tbears.icon.foundation/iconcommons/ --acl public-read
      aws s3 cp dist/*$VER*.whl s3://tbears.icon.foundation/iconcommons/ --acl public-read

    fi
  fi

else
  echo "Usage: build.sh [test|build|deploy]"
  echo "  test: run test"
  echo "  build: run test and build"
  echo "  build --ignore-test: run build"
  echo "  deploy: run test, build and deploy to s3"
  echo "  deploy --ignore-test: run build and deploy to s3"
  exit 1
fi
