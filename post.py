import util.main as main
import sqlite3, pandas
import util.dbutils as dbutils
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pylab

def query2df(meta, filter, tablename, database='iquod.db'):
    '''
    meta: list of strings of metadata to extract
    filter: string describing WHERE filter for SQL query, such as:
        'uid==1234'
        'cruise!=99 and month==10' etc
    tablename: sql table to extract from
    database: filename of database file

    return a dataframe with columns for every QC test plus specified metadata.
    also parses out truth if requested in the metadata list
    '''

    # get qc tests
    testNames = main.importQC('qctests')

    # connect to database
    conn = sqlite3.connect(database, isolation_level=None)
    cur = conn.cursor()

    # extract matrix of test results into a dataframe
    query = 'SELECT '
    if len(meta) > 0:
        query += ','.join(meta) + ','
    query += ','.join(testNames) + ' FROM ' + tablename
    if filter:
        query += ' WHERE ' + filter
    cur.execute(query)
    rawresults = cur.fetchall()
    df = pandas.DataFrame(rawresults).astype('str')
    df.columns = meta + testNames
    for t in testNames:
        df[[t]] = df[[t]].apply(dbutils.parse)

    # deal with truth data if present
    # column 'leveltruth' will persist per-level truth,
    # while 'Truth' summarizes by or'ing all levels together
    if 'truth' in meta:
        def unpack_truth(results):
            return results.apply(dbutils.unpack_qc)
        truth = df[['truth']].apply(unpack_truth).values.tolist()
        df = df.assign(leveltruth=pandas.Series(truth))
        df[['truth']] = df[['truth']].apply(dbutils.parse_truth)

    return df

def why_flag(uid, tests, tablename, database='iquod.db'):
    '''
    uid: int uid of profile in question
    tests: list of test names or combinations of tests joind by &
    tablename: sql table to extract from
    database: filename of database file

    determine which tests caused profile to be flagged.
    '''

    df = query2df([], 'uid='+str(uid), tablename, database)

    triggers = []
    for test in tests:
        qctests = test.split('&')
        flag = True
        for qctest in qctests:
            flag = flag & df.ix[0][qctest]
        if flag:
          triggers.append(test)

    return triggers

def construct_discrim(tests):
    '''
    tests: list of test names or combinations of tests joind by &

    return a function that accepts a qc database row as an argument and
    evaluates the qc assessment described by the 'tests' list
    '''

    def e(row):
        result = False
        for t in tests:
            qcs = t.split('&')
            term = True
            for qc in qcs:
                term = term and row[qc]
            result = result or term
        return result

    return e

def append_category(tests, tablename, database='iquod.db'):
    '''
    tests: list of test names or combinations of tests joind by &
    tablename: sql table to extract from
    database: filename of database file

    add a column 'category' to a qc table that indicates whether a profile is correctly or incorrectly flagged by
    the tests array from an analyze-results or catchall output, encoded as:
    0 == true positive
    1 == true negative
    2 == false positive
    3 == false negative
    '''

    # extract dataframe and apply discriminator
    #df = query2df(['truth', 'uid'], '', tablename, database)
    df = dbutils.db_to_df(tablename, filter_on_tests={'Remove rejected levels': ['CSIRO_depth', 'CSIRO_wire_break']})
    discriminator = construct_discrim(tests)
    df['qc'] = df.apply(discriminator, axis=1)

    # create empty 'category' column in db
    conn = sqlite3.connect(database, isolation_level=None)
    cur = conn.cursor()
    #query = 'ALTER TABLE ' + tablename + ' ADD category integer;'
    #cur.execute(query)

    # write results to database
    def update_db(row):
        if row['qc'] and row['Truth']:
            category = 0
        elif not row['qc'] and not row['Truth']:
            category = 1
        elif row['qc'] and not row['Truth']:
            category = 2
        elif not row['qc'] and row['Truth']:
            category = 3
        query = 'UPDATE ' + tablename +  ' SET category = ' + str(category) + ' WHERE uid=' + str(row['uid'])
        cur.execute(query)
    df.apply(update_db, axis=1)

def dump_row(uid, table, database='iquod.db'):
    '''
    print all database keys and values for uid
    '''

    # extract and parse row
    conn = sqlite3.connect(database, isolation_level=None)
    cur = conn.cursor()
    query = 'SELECT * FROM ' + table +' WHERE uid=' + str(uid)
    cur.execute(query)
    rawresults = cur.fetchall()
    df = pandas.DataFrame(rawresults).astype('str')
    df.columns = [description[0] for description in cur.description]
    testNames = main.importQC('qctests')
    testNames = [t.lower() for t in testNames]
    for t in testNames:
        df[[t]] = df[[t]].apply(dbutils.parse)
    df[['truth']] = df[['truth']].apply(dbutils.parse_truth)

    for col in list(df):
        print col, ':', df.ix[0][col]


def plot_uid(uid, table, database='iquod.db'):

    # extract and parse row
    conn = sqlite3.connect(database, isolation_level=None)
    cur = conn.cursor()
    query = 'SELECT * FROM ' + table +' WHERE uid=' + str(uid)
    cur.execute(query)
    rawresults = cur.fetchall()
    df = pandas.DataFrame(rawresults).astype('str')
    df.columns = [description[0] for description in cur.description]
    testNames = main.importQC('qctests')
    testNames = [t.lower() for t in testNames]
    for t in testNames:
        df[[t]] = df[[t]].apply(dbutils.parse)
    def unpack_truth(results):
        return results.apply(dbutils.unpack_qc)
    truth = df[['truth']].apply(unpack_truth).values.tolist()
    df = df.assign(leveltruth=pandas.Series(truth))
    df[['truth']] = df[['truth']].apply(dbutils.parse_truth)

    plotRow(df.ix[0], '.')

def plotRow(row, figdir):
    '''
    generate a plot of the profile in QC table <row>
    <row> must include the raw profile text and the per-level truth
    fig saved as figdir/uid.png
    row should have 'raw' and 'leveltuth' cols
    '''

    p = main.text2wod(row['raw'][1:-1])
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    im = ax1.scatter(p.z(),p.t(), c=row['leveltruth'][0], norm=matplotlib.colors.Normalize(vmin=1, vmax=10), cmap='tab10')
    fig.colorbar(im, ax=ax1)
    plt.xlabel('Depth [m]')
    plt.ylabel('Temperature [C]')
    plt.title(str(p.uid()))
    range = plt.ylim()
    plt.ylim(max(-10, range[0]), min(40, range[1]))
    range = plt.ylim()
    dom = plt.xlim()
    plt.xlim(max(-10, dom[0]), min(10000, dom[1]))
    dom = plt.xlim()
    xmargin = (dom[1] - dom[0])*0.7 + dom[0]
    yspace = (range[1] - range[0])*0.05
    ymargin = (range[1] - range[0])*0.95 + range[0]
    plt.text(xmargin,ymargin - 2*yspace, 'Lat: ' + str(p.latitude()))
    plt.text(xmargin,ymargin - 3*yspace, 'Long: ' + str(p.longitude()))
    plt.text(xmargin,ymargin - 4*yspace, 'Probe: ' + str(p.probe_type()))
    plt.text(xmargin,ymargin - 5*yspace, 'Date: ' + str(p.year()) + '/' + str(p.month()) + '/' + str(p.day())    )
    plt.text(xmargin,ymargin - 6*yspace, 'Originator: ' + str(p.originator_flag_type()))
    plt.text(xmargin,ymargin - 7*yspace, 'Instrument: ' + str(probe_detail(p)))
    pylab.savefig(figdir + '/' + str(p.uid()) + '.png', bbox_inches='tight')
    plt.close()


def plot_uid_pathology(uid, table, database='iquod.db'):

    # extract and parse row
    conn = sqlite3.connect(database, isolation_level=None)
    cur = conn.cursor()
    query = 'SELECT * FROM ' + table +' WHERE uid=' + str(uid)
    cur.execute(query)
    rawresults = cur.fetchall()
    df = pandas.DataFrame(rawresults).astype('str')
    df.columns = [description[0] for description in cur.description]
    testNames = main.importQC('qctests')
    testNames = [t.lower() for t in testNames]
    for t in testNames:
        df[[t]] = df[[t]].apply(dbutils.parse)
    def unpack_truth(results):
        return results.apply(dbutils.unpack_qc)
    truth = df[['truth']].apply(unpack_truth).values.tolist()
    df = df.assign(leveltruth=pandas.Series(truth))
    df[['truth']] = df[['truth']].apply(dbutils.parse_truth)

    plotPathology(df.ix[0], '.')

def plotPathology(row, figdir):
    '''
    look for a transition from all good to all bad, and plot that region
    just do plotRow if no such transition is found. 
    '''

    p = main.text2wod(row['raw'][1:-1])
    def cat(flag):
        if flag == 3 or flag == 4:
            return True
        else:
            return False
    category = [cat(x) for x in row['leveltruth'][0]]
    total = sum(category)
    if sum(category[len(category)-total:]) != total:
        plotRow(row, figdir)
        return 0

    z_transition = p.z()[len(category) - total]
    t_transition = p.t()[len(category) - total]

    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    im = ax1.scatter(p.z(),p.t(), c=row['leveltruth'][0], norm=matplotlib.colors.Normalize(vmin=1, vmax=10), cmap='tab10')
    fig.colorbar(im, ax=ax1)
    plt.xlabel('Depth [m]')
    plt.ylabel('Temperature [C]')
    plt.title(str(p.uid()))
    range = plt.ylim()
    plt.ylim(t_transition-1, t_transition+1 )
    range = plt.ylim()
    dom = plt.xlim()
    plt.xlim(z_transition-20, z_transition+20)
    dom = plt.xlim()
    xmargin = (dom[1] - dom[0])*0.7 + dom[0]
    yspace = (range[1] - range[0])*0.05
    ymargin = (range[1] - range[0])*0.95 + range[0]
    plt.text(xmargin,ymargin - 2*yspace, 'Lat: ' + str(p.latitude()))
    plt.text(xmargin,ymargin - 3*yspace, 'Long: ' + str(p.longitude()))
    plt.text(xmargin,ymargin - 4*yspace, 'Probe: ' + str(p.probe_type()))
    plt.text(xmargin,ymargin - 5*yspace, 'Date: ' + str(p.year()) + '/' + str(p.month()) + '/' + str(p.day())    )
    plt.text(xmargin,ymargin - 6*yspace, 'Originator: ' + str(p.originator_flag_type()))
    plt.text(xmargin,ymargin - 7*yspace, 'Instrument: ' + str(probe_detail(p)))
    pylab.savefig(figdir + '/' + str(p.uid()) + '.png', bbox_inches='tight')
    plt.close()

def probe_detail(p):
    '''
    given a wodpy profile p,
    find the instrument type index from table 3.2 in the wodpy docs
    '''

    varspecmeta = p.primary_header['variables']
    for var in varspecmeta:
        if var['Variable code'] != 1:
            continue
        for meta in var['metadata']:
            if meta['Variable-specific code'] == 5:
                return meta['Value']

    return None



