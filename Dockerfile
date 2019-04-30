# Set the base image to Ubuntu, use a public image
FROM continuumio/miniconda3 as builder

# File Author / Maintainer
MAINTAINER Thomas Schmelzer "thomas.schmelzer@lobnek.com"

COPY . /tmp/pyutil

RUN conda install -y -c conda-forge nomkl pandas=0.24.2 cvxpy=1.0.15 requests=2.21.0 xlrd xlsxwriter && \
    conda clean -y --all && \
    pip install --no-cache-dir -r /tmp/pyutil/requirements.txt && \
    pip install --no-cache-dir /tmp/pyutil && \
    rm -r /tmp/pyutil

#### Here the test-configuration
FROM builder as test

# We install flask here to test some
RUN pip install --no-cache-dir httpretty pytest==4.3.1 pytest-cov pytest-html sphinx flask==1.0.2

WORKDIR /pyutil

CMD py.test --cov=pyutil  --cov-report html:artifacts/html-coverage --cov-report term --html=artifacts/html-report/report.html test