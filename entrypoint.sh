# ===================================================
# 1. run experimental qc tests mounted at /AutoQC/dev
# ===================================================

# move tests into position
cp /AutoQC/dev/qctests/* /AutoQC/qctests/.

# make columns for tests in iquod table
python amend_columns.py /AutoQC/dev/qctests

# munge AutoQC.py to only run these new tests
TESTS="testNames="$(ls /AutoQC/dev/qctests | sed -e 's|\.py$||'| awk ' BEGIN { ORS = ""; print "["; } { print "\""$0"\","; } END { print "]"; }' | sed -e 's|,]$|]|')
sed -i "s|testNames\.sort()|${TESTS}|g" AutoQC.py

# run experimental tests
python AutoQC.py quota 4

# keep logs
mv autoqc-logs* /AutoQC/dev/.

# ========================
# 2. run summarize-results
# =======================

python summarize-results.py quota > summarize-results.dat
mv summarize-results.dat /AutoQC/dev/summarize-results.dat

# ===============
# 3. run catchall
# ===============

python catchall.py quota 10000
cp catchall.json /AutoQC/dev/.

# ==========================
# 4. generate category plots
# ==========================

mkdir /AutoQC/dev/plots
mkdir TP
mkdir TN
mkdir FP
mkdir FN
python plots.py
mv TP /AutoQC/dev/plots/.
mv TN /AutoQC/dev/plots/.
mv FP /AutoQC/dev/plots/.
mv FN /AutoQC/dev/plots/.

# ====================
# 5. record final perf
# ====================

echo 'TP: ' > /AutoQC/dev/perf.dat
sqlite3 iquod.db 'select count(*) from quota where training=0 and category=0' >> /AutoQC/dev/perf.dat
echo 'TN: ' >> /AutoQC/dev/perf.dat
sqlite3 iquod.db 'select count(*) from quota where training=0 and category=1' >> /AutoQC/dev/perf.dat
echo 'FP: ' >> /AutoQC/dev/perf.dat
sqlite3 iquod.db 'select count(*) from quota where training=0 and category=2' >> /AutoQC/dev/perf.dat
echo 'FN: ' >> /AutoQC/dev/perf.dat
sqlite3 iquod.db 'select count(*) from quota where training=0 and category=3' >> /AutoQC/dev/perf.dat

# =================
# 6. system logging
# =================

git log > /AutoQC/dev/gitlogs.dat
pip freeze > /AutoQC/dev/pipfreeze.dat
