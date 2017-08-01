try:
  import _pickle as cPickle
except ImportError:
  import pickle as cPickle

def deepcopy(obj):
  return cPickle.loads(cPickle.dumps(obj))