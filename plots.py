import util.post as post
import util.main as main
import json, sqlite3

with open('catchall.json') as json_data:
    d = json.load(json_data)
tests = d['tests']
tablename = 'quota'

# add TP/TN/FP/FN category column
post.append_category(tests, tablename)

# plotting subsets
df = post.query2df(['raw', 'truth'], 'category=0 and training=0', tablename)
df.apply(post.plotRow, axis=1, args=('TP',))
df = post.query2df(['raw', 'truth'], 'category=1 and training=0', tablename)
df.apply(post.plotRow, axis=1, args=('TN',))
df = post.query2df(['raw', 'truth'], 'category=2 and training=0', tablename)
df.apply(post.plotRow, axis=1, args=('FP',))
df = post.query2df(['raw', 'truth'], 'category=3 and training=0', tablename)
df.apply(post.plotRow, axis=1, args=('FN',))
