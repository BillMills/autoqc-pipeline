for i in 0 1 2 3 4 5 6 7 8 9
do
  bash optimize-classifier.sh $i
done

python perf-uncertainty.py 10 > dev/perf-uncertainty.dat
