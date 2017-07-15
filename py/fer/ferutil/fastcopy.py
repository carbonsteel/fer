import _pickle as cPickle

def deepcopy(obj):
  return cPickle.loads(cPickle.dumps(obj))