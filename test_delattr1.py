from demo import delattr1

o = delattr1.Child()
print o.__dict__
o.x = 'x'
print o.__dict__
o.parse()
print o.__dict__
del o.x
print o.__dict__
del o._unrecognized_args
print o.__dict__
