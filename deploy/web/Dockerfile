FROM debian:latest
ENV SET_CONTAINER_TIMEZONE true
ENV CONTAINER_TIMEZONE Europe/Zurich
ENV TZ Europe/Zurich
RUN mkdir /install
COPY ./requirements.txt /install 
COPY ./conda_packages.txt /install 
WORKDIR /install
RUN apt-get update --fix-missing && \ 
    apt-get install -y wget bzip2 ca-certificates \
    libglib2.0-0 libxext6 libsm6 libxrender1 libmariadbclient-dev build-essential \ 
    && apt-get autoremove \ 
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
RUN echo 'export PATH=/opt/conda/bin:$PATH' > /etc/profile.d/conda.sh \
    && wget --quiet https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh \
    && /bin/bash ~/miniconda.sh -b -p /opt/conda \
    && rm ~/miniconda.sh
ENV PATH /opt/conda/bin:$PATH
# Use append to add conda-forge at the end of channels
# conda config --append channels conda-forge \
# Seems to be a bad idea to mix defaults and conda-forge channels
RUN conda config --add channels bokeh \
    && conda install --file /install/conda_packages.txt \
    && conda clean -i -l -t -y
RUN pip install -r /install/requirements.txt \
    && rm -rf /root/.cache/pip/*
CMD ["python"]
#, "manage.py", "runserver", "0.0.0.0:8008"]
