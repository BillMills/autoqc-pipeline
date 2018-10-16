import util.post as post
import json

with open('catchall.json') as json_data:
    d = json.load(json_data)
tests = d['tests']
tablename = 'quota'

# add TP/TN/FP/FN category column
post.append_category(tests, tablename)
