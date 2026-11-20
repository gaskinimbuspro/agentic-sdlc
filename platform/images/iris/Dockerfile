# Image for Iris's workflow steps. Wheels are built beforehand (see build.sh),
# so the image build needs no network beyond the base image.
# The full Debian-based Python image already contains git.
FROM python:3.12.14-bookworm
COPY wheels/ /tmp/wheels/
RUN pip install --no-cache-dir --no-index --find-links /tmp/wheels backend-standard \
    && rm -rf /tmp/wheels \
    && useradd --uid 1000 --create-home iris
USER 1000
ENV HOME=/tmp
WORKDIR /work
