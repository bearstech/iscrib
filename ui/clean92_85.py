"""
Replace the bad windows cut and past caracter:
'\x92' by "'" and '\x85' by "..."
"""
import os
for file in os.listdir('.'):
  #print file
  if file.endswith('ml'):
      data = open(file, 'r').readlines()
      lines92 = [l for l in data if l.count('\x92')]
      lines85 = [l for l in data if l.count('\x85')]
      if lines92:
          print '92', file, len(lines92)
          res = []
          for l in open(file, 'r').readlines():
              if l.count('\x92'):
                  l = l.replace('\x92' ,"'")
              res.append(l)
          open(file, 'w').write(''.join(res))

      if lines85:
          print '85', file, len(lines85)
          res = []
          for l in open(file, 'r').readlines():
              if l.count('\x85'):
                  l = l.replace('\x85', "...")
              res.append(l)
          open(file, 'w').write(''.join(res))

