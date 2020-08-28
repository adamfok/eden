import os

UTILS_PATH = os.path.dirname(__file__)
EDEN_PATH = os.path.dirname(UTILS_PATH)
SCRIPTS_PATH = os.path.dirname(EDEN_PATH)
DATA_PATH = os.path.abspath(os.path.join(SCRIPTS_PATH, "..", "data"))

RELOAD_DIRS = [os.path.join(EDEN_PATH, "core"),
               os.path.join(EDEN_PATH, "utils"),
               os.path.join(EDEN_PATH, "maya_tools")]


def getModPath(filepath):
    module_name = os.path.basename(filepath).split(".py")[0]
    _module_path = os.path.dirname(filepath).split(os.path.dirname(SCRIPTS_PATH))[-1].split('\\')[2:]
    module_path = ".".join(_module_path)
    return module_path, module_name


def reloadModules(*args):
    for reload_dir in RELOAD_DIRS:
        for root, dirs, files in os.walk(reload_dir):
            for f in files:
                if not f.startswith("_") and f.endswith(".py"):
                    path = os.path.join(root, f)

                    module_path, module_name = getModPath(path)

                    try:
                        mod = __import__("%s.%s" % (module_path, module_name), (), (), [module_name])
                        reload(mod)

                        print ("Reload {}".format(mod))

                    except Exception as e:
                        print ('Reload Failed %s : \n\t\t\t%s' % (module_name, e))
                        pass
