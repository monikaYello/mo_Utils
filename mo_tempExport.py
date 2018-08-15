
import pymel.core as pm

def tempExportSelected(save_name = 'tempExport', path = "U:/personal/Monika/tempExport" ):
    pm.cmds.file("%s/%s.ma"%(path,save_name), pr=1, typ="mayaAscii", force=1, options="v=0;", es=1)

def tempImport( save_name = 'tempExport', path = "U:/personal/Monika/tempExport"):
    pm.cmds.file("%s/%s.ma"%(path,save_name), pr=1, ignoreVersion=1, i=1, type="mayaAscii",
              namespace=":", ra=True, mergeNamespacesOnClash=True, options="v=0;")
