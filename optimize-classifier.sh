cp /AutoQC/dev/qctests/* /AutoQC/qctests/.

if [ "$CUSTOM_PERF" = "1" ]
then
  cp /AutoQC/dev/custom_perf.json catchall.json
else
  python catchall.py quota 10000
  cp catchall.json /AutoQC/dev/.
fi

python classify-profiles.py

echo 'TP: ' > /AutoQC/dev/perf${1}.dat
sqlite3 iquod.db 'select count(*) from quota where training=0 and category=0' >> /AutoQC/dev/perf${1}.dat
echo 'TN: ' >> /AutoQC/dev/perf${1}.dat
sqlite3 iquod.db 'select count(*) from quota where training=0 and category=1' >> /AutoQC/dev/perf${1}.dat
echo 'FP: ' >> /AutoQC/dev/perf${1}.dat
sqlite3 iquod.db 'select count(*) from quota where training=0 and category=2' >> /AutoQC/dev/perf${1}.dat
echo 'FN: ' >> /AutoQC/dev/perf${1}.dat
sqlite3 iquod.db 'select count(*) from quota where training=0 and category=3' >> /AutoQC/dev/perf${1}.dat
