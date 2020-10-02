FROM fedora:latest
ARG TWINE_USERNAME=__token__
ARG TWINE_PASSWORD=""
ARG TWINE_REPOSITORY=testpypi

RUN dnf -y install python36 python37 python38 python3-pip python3-tox gnupg2 && \
    dnf -y clean all && \
    rm -rf /var/cache/dnf

COPY setup.py               /app/setup.py
COPY tox.ini                /app/tox.ini
COPY src/osdk_manager       /app/src/osdk_manager
COPY tests                  /app/tests
WORKDIR                     /app

RUN tox && \
    tox -e release
