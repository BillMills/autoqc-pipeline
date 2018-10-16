import numpy, sys

# order: TP, TN, FP, FN
counts = [[],[],[],[]]

for i in range(int(sys.argv[1])):
    with open('dev/perf' + str(i) + '.dat') as f:
        for j in range(4):
            l = f.readline()
            count = int(f.readline())
            counts[j].append(count)

TP  = numpy.mean(counts[0])
dTP = numpy.std(counts[0])

TN  = numpy.mean(counts[1])
dTN = numpy.std(counts[1])

FP  = numpy.mean(counts[2])
dFP = numpy.std(counts[2])

FN  = numpy.mean(counts[3])
dFN = numpy.std(counts[3])

TPR = TP / (TP + FN)
dTPR = TPR*((dTP/TP)**2 + ( ((dTP*dTP + dFN*dFN)**0.5) / (TP+FN) )**2)**0.5

FPR = FP / (FP + TN)
dFPR = FPR*((dFP/FP)**2 + ( ((dFP*dFP + dTN*dTN)**0.5) / (FP+TN) )**2)**0.5

print 'TPR:', TPR, '+-', dTPR
print 'FPR:', FPR, '+-', dFPR
