import cPickle as pick

print ("ok")
byte = []
st = "ABC"
byte = pick.dumps(st)
print(byte)

print(pick.loads(byte))