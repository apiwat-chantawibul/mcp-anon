FROM python:3.13

ARG USERNAME=non-root
ARG USER_UID=10000
ARG USER_GID=$USER_UID
ARG BASE_DIR=/opt/app

# Create non-root user
RUN <<EOF
set -eux
groupadd --gid $USER_GID $USERNAME
useradd --uid $USER_UID --gid $USER_GID -m $USERNAME
EOF

# Install libraries
WORKDIR $BASE_DIR
COPY requirements.txt pip-freeze.txt ./
RUN <<EOF
set -eux
pip install --no-cache-dir --upgrade -r requirements.txt -r pip-freeze.txt
rm requirements.txt pip-freeze.txt
EOF

# Install application source code
WORKDIR $BASE_DIR/src
COPY src ./
ENV PYTHONPATH=$BASE_DIR/src

# Switch to non-root executing user, prepare write-able workdir.
USER $USER_UID
WORKDIR $BASE_DIR/workdir
ENTRYPOINT ["python", "-m", "app"]
CMD []

