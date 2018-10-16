cp /AutoQC/dev/qctests/* /AutoQC/qctests/.

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


