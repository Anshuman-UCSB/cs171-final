import pickle

l = [1,2,3]
x = pickle.dumps(l)

print(pickle.loads(x))
l[2]=5
print(pickle.loads(x))