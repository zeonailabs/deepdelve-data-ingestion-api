# Define custom function directory
ARG FUNCTION_DIR="/function"

FROM public.ecr.aws/docker/library/python:3.8-buster as build-image
#FROM python:buster as build-image
# Include global arg in this stage of the build
ARG FUNCTION_DIR

# Copy function code
RUN mkdir -p ${FUNCTION_DIR}


# Install the function's dependencies
RUN pip install \
    --target ${FUNCTION_DIR} \
        awslambdaric


FROM public.ecr.aws/docker/library/python:3.8-buster

# Install aws-lambda-cpp build dependencies
RUN apt-get update && \
  apt-get install -y \
  g++ \
  make \
  cmake \
  unzip \
  libcurl4-openssl-dev \
  software-properties-common \
  libjpeg-dev \
  libtiff-dev \
  libpng-dev

RUN apt-get -y install \
    ghostscript \
    libleptonica-dev \
    icc-profiles-free \
    libxml2 \
    pngquant \
    python3-distutils \
    python3-pkg-resources \
    python3-reportlab \
    qpdf \
    zlib1g \
    unpaper

# Include global arg in this stage of the build
ARG FUNCTION_DIR
# Set working directory to function root directory
WORKDIR ${FUNCTION_DIR}

ENV AWS_LAMBDA_FUNCTION_TIMEOUT=216000

COPY requirements.txt ${FUNCTION_DIR}
RUN pip install -r requirements.txt

RUN SKLEARN_ALLOW_DEPRECATED_SKLEARN_PACKAGE_INSTALL=True

COPY rest_api ${FUNCTION_DIR}/rest_api
COPY __init__.py ${FUNCTION_DIR}

# Copy in the built dependencies
COPY --from=build-image ${FUNCTION_DIR} ${FUNCTION_DIR}

#COPY ./entry_script.sh /entry_script.sh
#RUN chmod +x /entry_script.sh
#ADD aws-lambda-rie /usr/local/bin/aws-lambda-rie
#ENTRYPOINT [ "/entry_script.sh" ]

ENTRYPOINT [ "/usr/local/bin/python", "-m", "awslambdaric" ]
CMD [ "rest_api.application.handler" ]