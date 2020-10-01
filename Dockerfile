FROM fedora:latest
RUN dnf -y install python36 python37 python38 python3-pip python3-tox && \
    dnf -y clean all && \
    rm -rf /var/cache/dnf

COPY src/operator_sdk_manager /app/src/operator_sdk_manager
COPY tests /app/tests
COPY setup.py /app/setup.py
COPY tox.ini /app/tox.ini
WORKDIR /app

ENV TWINE_USERNAME=__token__ \
    TWINE_PASSWORD="" \
    TWINE_REPOSITORY=testpypi

RUN tox
