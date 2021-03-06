#!/bin/bash

BASENAME=`basename $0`
CUR_DIR=`dirname $0`
VENV_DIR=`readlink -f $CUR_DIR/.env`
echo $VENV_DIR

pushd "$CUR_DIR/uwsgi"
UWSGI_CMD="$VENV_DIR/bin/uwsgi uwsgi_dev.xml"
$UWSGI_CMD
popd
