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

# summarize individual test performance
python summarize-results.py quota > summarize-results.dat
mv summarize-results.dat /AutoQC/dev/summarize-results.dat

# system logging

git log > /AutoQC/dev/gitlogs.dat
pip freeze > /AutoQC/dev/pipfreeze.dat
