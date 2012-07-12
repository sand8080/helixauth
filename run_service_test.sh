#!/bin/bash

BASENAME=`basename $0`
CUR_DIR=`dirname $0`
VENV_DIR=`readlink -f $CUR_DIR/../.venv_helix`
echo $VENV_DIR

pushd "$CUR_DIR/uwsgi"
UWSGI_CMD="$VENV_DIR/bin/uwsgi uwsgi_test.xml"
$UWSGI_CMD
popd
