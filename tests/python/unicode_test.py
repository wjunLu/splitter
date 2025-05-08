import sys

open(u'h\xe9llo', 'w')
print(sys.getfilesystemencoding())
assert 'utf-8' == sys.getfilesystemencoding()
print(u'h\xe9llo.txt')
assert u'h\xe9llo.txt' == 'héllo.txt'
print("Unicode test successfully!")
