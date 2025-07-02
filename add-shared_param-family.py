from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import TaskDialog
from Autodesk.Revit.UI.Selection import ObjectType
from Autodesk.Revit.Exceptions import InvalidOperationException


__title__ = 'Nuvolo\n Shared Parameters'

# Get current doc and app
uidoc = __revit__.ActiveUIDocument
doc = uidoc.Document
app = __revit__.Application

# --- SETTINGS ---
shared_param_file_path = r"write file path to the shared parameters file"
shared_param_group_name = "write the group name of the parameters"
shared_param_names = [
    "param #1",
    "param #2"
]

# --- FUNCTIONS ---

def get_shared_parameter_definition(app, group_name, param_name):
    app.SharedParametersFilename = shared_param_file_path
    shared_param_file = app.OpenSharedParameterFile()
    if not shared_param_file:
        TaskDialog.Show("Error", "Shared Parameter file not found or invalid!")
        return None

    for group in shared_param_file.Groups:
        if group.Name == group_name:
            for definition in group.Definitions:
                if definition.Name == param_name:
                    return definition
    return None

def add_multiple_shared_params_to_family(fam_doc, param_defs):
    fam_mgr = fam_doc.FamilyManager
    existing_params = [p.Definition.Name for p in fam_mgr.Parameters]

    for param_def in param_defs:
        if param_def.Name in existing_params:
            TaskDialog.Show("Info", "Parameter '{}' already exists.".format(param_def.Name))
            continue

        fam_mgr.AddParameter(param_def, BuiltInParameterGroup.PG_IDENTITY_DATA, True)
        TaskDialog.Show("Success", "Added parameter '{}'.".format(param_def.Name))

# --- MAIN SCRIPT ---

try:
    # Pick a family instance
    ref = uidoc.Selection.PickObject(ObjectType.Element, "Select a family instance")
    element = doc.GetElement(ref)
    family = element.Symbol.Family

    # Open family doc
    fam_doc = doc.EditFamily(family)

    # Collect all param defs first
    param_defs = []
    for param_name in shared_param_names:
        param_def = get_shared_parameter_definition(app, shared_param_group_name, param_name)
        if not param_def:
            TaskDialog.Show("Error", "Parameter '{}' not found in Shared Parameter file.".format(param_name))
            fam_doc.Close(False)
            raise Exception("Parameter '{}' missing".format(param_name))
        param_defs.append(param_def)

    # Add all parameters in one transaction
    t = Transaction(fam_doc, "Add Shared Parameters")
    t.Start()
    add_multiple_shared_params_to_family(fam_doc, param_defs)
    t.Commit()

    # Reload into project
    fam_doc.LoadFamily(doc)
    fam_doc.Close(False)

except InvalidOperationException:
    TaskDialog.Show("Cancelled", "Operation cancelled or invalid selection.")
except Exception as e:
    TaskDialog.Show("Error", str(e))
