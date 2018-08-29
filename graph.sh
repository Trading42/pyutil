#!/usr/bin/env bash

package='pyutil'

mkdir -p artifacts/graph

docker run --rm \
       --mount type=bind,source=$(pwd)/${package},target=/pyan/${package},readonly \
       tschm/pyan:latest \
       python pyan.py ${package}/**/*.py -V --uses --defines --colored --dot --nested-groups \
       > graph.dot   # this is the output of the docker run command. It's writtern directly to the host

docker run --rm \
       -v $(pwd)/graph.dot:/pyan/graph.dot:ro \
       tschm/pyan:latest \
       dot -Tsvg /pyan/graph.dot > artifacts/graph/graph.svg

rm -f graph.dot

