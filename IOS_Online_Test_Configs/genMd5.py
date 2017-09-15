#!/usr/bin/python
import os
import hashlib, json, re
import pickle

# set script path
enpth = os.path.split(os.path.realpath(__file__))[0]
os.chdir(enpth)

# define
tree_bin = 'tree.bin'
fJson = 'diff.json'


def get_md5(ct):
    md5 = hashlib.md5()
    md5.update(ct)
    return md5.hexdigest()


def gen_tree(epath):
    _tree = {}
    for root, dirs, files in os.walk(epath):
        for x in files:
            sufix = os.path.splitext(x)[1][1:]
            if sufix == r'json':
		if x != fJson:
                	f = open(x, 'r')
                	_tree[x] = get_md5(f.read())
                	f.close()
    return _tree


def write_bin(ct, treefile):
    f = open(treefile, 'w')
    pickle.dump(ct, f)
    f.close()


def get_tree_bin(treebin):
    f = file(treebin)
    _tree = pickle.load(f)
    f.close()
    return _tree


def cpr_file(ortree, nwtree):
    for x in nwtree:
        try:
            if nwtree[x] != ortree[x]:
                print x + 'changed'
                return False
        except:
            print 'crab'
            return False

    print 'for done'
    return True


def rj2f():
    _tree = gen_tree(enpth)
    write_bin(_tree, tree_bin)
    _jcontent = json.dumps(_tree)
    f = file(fJson, 'w')
    f.write(_jcontent)
    f.close()


# if the first time to run this script
if not os.path.exists(tree_bin):
    print 'is first time'
    rj2f()
else:
    ortree = get_tree_bin(tree_bin)
    nwtree = gen_tree(enpth)
    if not cpr_file(ortree, nwtree):
        print 'gen new json'
        rj2f()
    else:
        print 'nothing new'
