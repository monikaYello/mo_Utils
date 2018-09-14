
def test(testvar):
    print 'this is a test'
    int_var = 12

    print 'test var is %s'%testvar

    print int_var

    return int_var




string_var = 'hello'
return_var = test(string_var)

import sys
sys.path.append('D:\Google Drive\PythonScripting\scripts')
import mo_UI.mo_UI as ui
reload(ui)
ui.mo_UI()

# import sys
# sys.path.append('D:\Google Drive\PythonScripting\scripts')
# import mo_UI.mo_UI as ui
# reload(ui)
# ui.mo_UI()