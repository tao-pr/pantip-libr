"""
Tapper utility for pipeline
@starcolon projects
"""

def printtext(str):
  def bypass(data):
    print(str)
    return data
  return bypass

def printdata(data):
  print(data)
  return data

# This only works if the data is a {list}
def zip_with(zipper,another,lazy=True):
  def zip_(data):
    if lazy: return map(zipper,data,another)
    else: return list(map(zipper,data,another))
  return zip_