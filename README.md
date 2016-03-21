# HONQ: Hierarchical Operating system Notation Query
Provides really easy to use filtering options for getting the files you want.
Iterate over Files(), optionally chaining additional filters to get what you
want without bothering with os.walk.

IMPORTANT NOTE: For processing speed, it returns (`full path`, `file name`).
End the query with .full() to limit the results to just the full path.

Prints out all the files in all sub directories of C:/CoolStuff

    for f in Files('C:/CoolStuff').full():
      print f
      
Use .skipFolders(), .like()/.notLike(), .types()/.notTypes() to filter results.
This finds all .jpg and .jpeg files under C:/CoolStuff, skipping and directories
with "temp" in the name.

    for f in Files('C:/CoolStuff').skipFolders('temp').types('jpg', 'jpeg').full():
        print f
      
.like()/.unlike() and .skipFolders(), in addtion to several criteria, can be
followed with exact=True to require an exact match, so .like('temp', exact=True)
only matches 'temp' and not 'temporal'

    for f in Files('C:/CoolStuff').skipFolders('temp', exact=True).full():
        print f
      
Case is ignore by default, controlled by the module variable `ignoreCase`

    honq.ignoreCase = False  # Now I'm case sensitive!
  
The search terms are actually regular expressions, you can get elaborate if needed.
This only finds files ending with song1, song2 and song3, only the top 3 are good
enough for us.

    for f in Files('C:/CoolStuff').like('song[1-3]').full():
        print f
