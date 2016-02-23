'''
Hierarchical Operating system Notation Query

Provides really easy to use filtering options for getting the files you want.
Iterate over Files(), optionally chaining additional filters to get what you
want without bothering with os.walk.

IMPORTANT NOTE: For processing speed, it returns (<full path>, <file name>).
End the query with .full() to limit the results to just the full path.




# Prints out all the files in all sub directories of C:/CoolStuff
for f in Files('C:/CoolStuff').full():
    print f

# Use .skipFolders(), .like()/.notLike(), .types()/.notTypes() to filter results.
# This finds all .jpg and .jpeg files under C:/CoolStuff, skipping and directories
# with "temp" in the name.
for f in Files('C:/CoolStuff').skipFolders('temp').types('jpg', 'jpeg').full():
    print f

# .like()/.unlike() and .skipFolders(), in addtion to several criteria, can be
# followed with exact=True to require an exact match, so .like('temp', exact=True)
# only matches 'temp' and not 'temporal'
for f in Files('C:/CoolStuff').skipFolders('temp', exact=True).full():
    print f

# Case is ignore by default, controlled by the module level `ignoreCase`
honq.ignoreCase = False  # Now I'm case sensitive!

# The search terms are actually regular expressions, you can get elaborate if needed.
# This only finds files ending with song1, song2 and song3, only top 3 is good
# enough for us.
for f in Files('C:/CoolStuff').like('song[1-3]').full():
    print f


'''


import itertools
import os
import re

try:
    import pathlib
except:
    pathlib = None


ignoreCase = True

        
class _Stream(object):
    '''
    Represents a stream of filenames.
    '''
    
    def __init__(self, upstream=None):
        self.incoming = upstream or tuple()
        
    def __iter__(self):
        return (i for i in self.incoming)
    
    def like(self, *patterns, **kwargs):
        '''
        Takes one or more patterns to match.  Optionally follow with exact=True.
        '''
        exact = kwargs['exact'] if 'exact' in kwargs else False
        return _Like(self, patterns, exact=exact)
    
    def notLike(self, *patterns, **kwargs):
        exact = kwargs['exact'] if 'exact' in kwargs else False
        return _Like(self, patterns, invert=True, exact=exact)

    def types(self, *filetypes):
        regexes = ['\.' + ft + '$' for ft in filetypes]
        return _Like(self, regexes, testFullPath=True)
    
    def notTypes(self, *filetypes):
        regexes = ['\.' + ft + '$' for ft in filetypes]
        return _Like(self, regexes, invert=True, testFullPath=True)
    
    #if pathlib:
    #    def asPathObj(self):
    #        return _ForEach(self, pathlib.Path)
    
    def fSlash(self):
        # Make results use forward slashes
        return _ForEach(self, lambda x: (x[0].replace('\\', '/'), x[1]) )
        
    def bSlash(self):
        # Make results use backslashes
        return _ForEach(self, lambda x: (x[0].replace('/', '\\'), x[1]) )
        
    def lower(self):
        # Make results lower case
        return _ForEach(self, lambda x: (x[0].lower(), x[1].lower()) )
    
    def full(self):
        # Limit results to the full filepath
        return _ForEach(self, lambda x: x[0] )
        
        
class _ForEach(_Stream):
    '''
    Runs the given function on the results.
    '''
    
    def __init__(self, upstream=tuple(), func=lambda x: x):
        super(_ForEach, self).__init__(upstream=upstream)
        self.func = func
    
    def __iter__(self):
        return itertools.imap(self.func, self.incoming)
    
                
class Files(_Stream):
    '''
    Takes one or more folders, returning all the files beneath it, and sub dirs.
    '''
    def __init__(self, *folders):
        '''
        init
        '''
        self.folders = [folder for folder in folders if os.path.isdir(folder)]
        self.ignore = None

    def __iter__(self):
        for folder in self.folders:
            for path, dirs, files in os.walk(folder):
                for f in files:
                    yield path + '/' + f, os.path.splitext(f)[0]
            
                if self.ignore:
                    toRemove = [d for d in dirs if self.ignore(d)]
                    for toRem in toRemove:
                        dirs.remove(toRem)
                
    def skipFolders(self, *folders, **kwargs):
        if 'exact' in kwargs and kwargs['exact']:
            #regex = '((' + ')|('.join( folders ) + '))'
            regex = '((^' + '$)|(^'.join( folders ) + '$))'
        else:
            regex = '((' + ')|('.join( folders ) + '))'
        
        flags = re.IGNORECASE if ignoreCase else 0
        self.ignore = re.compile(regex, flags=flags).search
        
        return self


'''
class Dirs(_Stream):
    
    def __init__(self, *folders):
        self.folders = [folder for folder in folders if os.path.isdir(folder)]
        self.ignore = None

    def __iter__(self):
        for folder in self.folders:
            for path, dirs, files in os.walk(folder):

                if self.ignore:
                    toRemove = [d for d in dirs if self.ignore(d)]
                    for toRem in toRemove:
                        dirs.remove(toRem)
                
                for d in dirs:
                    yield path + '/' + d
                
    def skipFolders(self, *folders):
        regex = '((' + ')|('.join( folders ) + '))'
        
        flags = re.IGNORECASE if ignoreCase else 0
        self.ignore = re.compile(regex, flags=flags).search
        
        return self
'''


class _Like(_Stream):
    '''
    Only allow files that pass the regexes (unless inverted).
    '''
    
    def __init__(self, upstream=tuple(), regexes=('.',), invert=False, exact=False, testFullPath=False):
        super(_Like, self).__init__(upstream=upstream)
        self.invert = invert
        
        if exact:
            regex = '((^' + '$)|(^'.join( regexes ) + '$))'
        else:
            regex = '((' + ')|('.join( regexes ) + '))'
        
        flags = re.IGNORECASE if ignoreCase else 0
        self.regex = re.compile(regex, flags).search
        
        if testFullPath:
            self.test = lambda (path, name): self.regex(path)
        else:
            self.test = lambda (path, name): self.regex(name)
        
    def __iter__(self):
        _stream = iter(self.incoming)
        if self.invert:
            return itertools.ifilterfalse(self.test, _stream)
        else:
            return itertools.ifilter(self.test, _stream)
