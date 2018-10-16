FROM iquod/autoqc:ubuntu-16.04

RUN apt-get install -y sqlite3

# prep AutoQC
RUN git reset --hard HEAD
RUN rm install.sh
RUN git pull origin master
COPY post.py /AutoQC/util/post.py
COPY amend_columns.py /AutoQC/amend_columns.py
COPY classify-profiles.py /AutoQC/classify-profiles.py
COPY plots.py /AutoQC/plots.py

# user scripts
COPY experimental-qc.sh experimental-qc.sh
COPY optimize-classifier.sh optimize-classifier.sh
COPY generate-plots.sh generate-plots.sh
COPY perf-uncertainty.py perf-uncertainty.py
COPY perf-uncertainty.sh perf-uncertainty.sh
