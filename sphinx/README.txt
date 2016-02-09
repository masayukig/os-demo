tox -d docs
# TODO,  you only need requirements, not build all docs
. .tox/docs/bin/activate
cp -r PATH/os-demo/sphinx/* docs
rm -rf doc/demo/html; sphinx-build -b html doc/demo/source doc/demo/html

# Copy in from review directory
rm -rf .tox/docs/lib/python2.7/site-packages/oslo_config/*
cp -r DIR/oslo_config/* .tox/docs/lib/python2.7/site-packages/oslo_config/

