import util.post as post

tablename = 'quota'

# plotting subsets
df = post.query2df(['raw', 'truth'], 'category=0 and training=0', tablename)
df.apply(post.plotRow, axis=1, args=('TP',))
df = post.query2df(['raw', 'truth'], 'category=1 and training=0', tablename)
df.apply(post.plotRow, axis=1, args=('TN',))
df = post.query2df(['raw', 'truth'], 'category=2 and training=0', tablename)
df.apply(post.plotRow, axis=1, args=('FP',))
df = post.query2df(['raw', 'truth'], 'category=3 and training=0', tablename)
df.apply(post.plotRow, axis=1, args=('FN',))
