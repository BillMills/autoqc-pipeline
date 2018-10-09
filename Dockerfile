FROM iquod/autoqc:ubuntu-16.04

RUN apt-get install -y sqlite3

# prep AutoQC
RUN git reset --hard HEAD
RUN rm install.sh
RUN git pull origin master
COPY iquod.redo_aoml_clim.db /AutoQC/iquod.db
COPY post.py /AutoQC/util/post.py
COPY amend_columns.py /AutoQC/amend_columns.py
COPY plots.py /AutoQC/plots.py

# default run script
COPY entrypoint.sh entrypoint.sh
CMD bash entrypoint.sh
