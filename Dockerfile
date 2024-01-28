ARG BASE_IMAGE_TAG=latest
FROM ghcr.io/pyvista/pyvista:$BASE_IMAGE_TAG

COPY . ${HOME}
WORKDIR ${HOME}
RUN pip install -r requirements.txt
RUN pip install -e . --no-deps  # to avoid pulling wrong VTK
