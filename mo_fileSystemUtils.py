import pymel.core as pm


def getFilesFromFolder(mypath):
    from os import listdir
    from os.path import isfile, join
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    return onlyfiles

# import mo_Utils.mo_fileSystemUtils as sysUtils
# sysUtils.addScriptPath('D:\Google Drive\PythonScripting\my_autoRigger')

def addScriptPath(dir):
    '''
    addScriptPath('')
    '''
    import os
    import sys
    # file = os.path.basename( module )
    # dir = os.path.dirname( module )
    # Check if dirrectory is really a dirrectory
    if (os.path.exists(dir)):

        # Check if the file dirrectory already exists in the sys.path array
        paths = sys.path
        pathfound = 0
        for path in paths:
            if (dir == path):
                pathfound = 1

        # If the dirrectory is not part of sys.path add it
        if not pathfound:
            sys.path.append(dir)
            print 'Sucessfully added to sys.path'
            print dir

        else:
            print 'Already in sys.path. Skipping.'
            print dir
    else:
        print 'Directory does not exist. Skipping.'
        return dir
    return paths


def clean_disappearingshelf_userprefs(path_to_userprefs, searchlines=[1000, 3000]):
    '''
    One reason for disappearing shelf buttons its entry exists multiple times in userPrefs.mel
    what confuses the loading. There might be a shelf entry with ; at the end and one without. Both valid
    but overwriting each other.

    This script runs through the .mel file and tries to remove any line with duplicates.
    Besides "shelfName" entries that are filtered are associated "shelfVersion", "shelfFile", "shelfLoad and
    "shelfAlign" entries
    Args:
        path_to_userprefs: file path to userPrefs.mel. Windows usually "C:/Users/username/Documents/maya/20xx/prefs/userPrefs.mel"
        searchlines:
            Limited to speed up script, if you need to modify will depend on  our file.
            Start and end line of  to process for search process. You can search "shelf" in userPrefs.mel
            in text editor to find the section
    Usage:
        Run the script, then reopen shelf (or restart maya)

        import mo_Utils.mo_fileSystemUtils as sysUtils
        sysUtils.clean_disappearingshelf_userprefs("C:/Users/monika/Documents/maya/2017/prefs/userPrefs.mel", searchlines=[2000, 2200])

    Returns: Error warning text or True

    '''
    import os
    if not os.path.isfile(path_to_userprefs):
        return pm.warning('Error. File not found (%s). Windows usually '
                          '"C:/Users/username/Documents/maya/20xx/prefs/userPrefs.mel"'%path_to_userprefs)

    # start and end line to filter search
    startline = searchlines[0]
    endline = searchlines[1]
    filepath = path_to_userprefs
    filepathnew = filepath.split('.mel')[0] + "New.mel"

    # this can be turned off for debugging and will leave the filtered file as filepath New.mel
    replace_with_backup=True

    # create new file
    open(filepathnew, "w+").close()

    with open(filepath, "r") as f, open(filepathnew, "a") as fnew:
        data = f.readlines()
        shelf_files = []
        skip_indices = []
        i = startline

        # - # find duplicates by looking for shelfName entries with same value
        # - # we store the shelf index as an int so we can also find and remove other linked
        # - # entries like shelfVersion and shelfFile
        for line in data[startline:endline]:
            words = line.split()
            if len(words) > 1:
                if words[1][1:10] == 'shelfName':
                    shelf_file = words[2].split('"')[1]

                    if shelf_file not in shelf_files:
                        print 'adding' + shelf_file
                        shelf_files.append(shelf_file)
                    else:
                        skip_indices.append(int(filter(str.isdigit, words[1])))  # add skip number

        # if no items were added to skip_indices, there i nothing to remove so we exit
        if len(skip_indices) == 0 :
            print 'No duplicate entries found. Try deleting and restoring the affected shelf manually.'
            os.remove(filepathnew)
            return False

        # - # adding the 1. block (till the startline) to the new file
        for line in data[:startline]:
            fnew.writelines(line)

        # - # 2. block, for each line, check for other setting for this shelf we need to remove via the Index
        # - # if it is not a duplicate we append the line to the new file
        for line in data[startline:endline]:
            skipline = False
            words = line.split()
            if len(words) > 1:
                if "shelfFile" in words[1] or "shelfAlign" in words[1] or "shelfLoad" in words[1] or "shelfVersion" in \
                        words[1] or "shelfName" in words[1]:
                    nrsearch = int(filter(str.isdigit, words[1]))
                    for sl in skip_indices:
                        if nrsearch == sl:
                            skipline = True

            # write if not skipping
            if skipline is False:
                fnew.writelines(line)
            else:
                print 'Duplicate found. Removing line %s' % words

            i += 1

        # - # adding the 3. block (everything after endline) to the new file
        for line in data[endline:]:
            fnew.writelines(line)

    # - # rename, backup old file .melOld
    if replace_with_backup:
        filepathold = filepath.split('.mel')[0] + ".melOld"
        os.rename(filepath, filepathold)
        os.rename(filepathnew, filepath)

    print 'Done. Removed %s duplicates. \n' \
          'New file: %s \nOld file backup: %s'%(len(skip_indices), filepath, filepathold)

    return True


def tempExportSelected(save_name = 'tempExport', path = "U:/personal/Monika/tempExport" ):
    pm.cmds.file("%s/%s.ma"%(path,save_name), pr=1, typ="mayaAscii", force=1, options="v=0;", es=1)

def tempImport( save_name = 'tempExport', path = "U:/personal/Monika/tempExport"):
    pm.cmds.file("%s/%s.ma"%(path,save_name), pr=1, ignoreVersion=1, i=1, type="mayaAscii",
              namespace=":", ra=True, mergeNamespacesOnClash=True, options="v=0;")

def transferShelfLowerVersion(mayashelfpath = 'C:/Users/dellPC/Documents/maya/2018/prefs/shelves/', shelfname = 'shelf_mo_Rig_shf', fromversion='2018', toversion='2016'):
    import os
    oldFilePath="%s%s.mel"%(mayashelfpath, shelfname)
    oldFile = open(oldFilePath, 'r')
    newFile = open(oldFilePath.replace(fromversion, toversion), 'w')
    lines = [line for line in oldFile.readlines() if line.strip()]
    itemskips = ['highlightColor', 'backgroundColor', 'flexibleWidthType', 'flexibleWidthValue', 'rotation', 'flipX', 'flipY', 'useAlpha']
    for line in lines:
        skipline = False   
        for itemskip in itemskips:
            if itemskip in line:
                skipline = True;
        
        if not skipline:
            newFile.write(line)
