"""
Author : Adam Chun Wai Fok
Date : Aug 2020

Description : 
    Custom Menu 2.0 using os.walk()
    
Note : 
    Script will walk through the custom menu path,
    dynamically create label divider on first level
    dynamically create sub-menu when folder found.
    dynamically create menuItem for each .py file, running .main() function of each file

"""
import maya.cmds as cmds
import maya.mel as mel
import os
import json


def install():
    print "Install Eden Custom Menu..."
    return


def uninstall():
    print "Un-Install Eden Custom Menu..."
    return


class CustomMenu(object):
    menu_root_path = os.path.dirname(__file__)
    root_path = os.path.abspath(os.path.join(menu_root_path, "..", ".."))
    main_menu = "eden_tools_menu"
    main_label = "Eden"

    def __init__(self):

        gMainWindow = mel.eval('$temp1 = $gMainWindow')

        if cmds.menu("eden_tools_menu", exists=True):
            cmds.deleteUI(self.main_menu)

        cmds.menu(self.main_menu, parent=gMainWindow, label=self.main_label, tearOff=True)

    def install(self):
        dir_path = os.path.dirname(__file__)
        dirs = [os.path.join(dir_path, f) for f in os.listdir(dir_path)]

        for d in [d for d in dirs if os.path.isdir(d)]:
            self.install_menu(d)

    def remove(self):
        if cmds.menu(self.main_menu, exists=True):
            cmds.deleteUI(self.main_menu)

    def take_order(self, elem):
        return elem[1]["order"]

    def install_menu(self, root_path, *args):
        item_infos = list()

        for item in os.listdir(root_path):
            path = os.path.join(root_path, item)

            if os.path.isdir(path):
                with open(os.path.join(path, "_menu_info.json")) as f:
                    info = json.load(f)

                item_infos.append([item, info])

        item_infos.sort(key=self.take_order)

        for item_info in item_infos:
            item, info = item_info
            path = os.path.join(root_path, item)

            if os.path.isdir(path) and info["hidden"] is False:
                print ('\n%s|| Menu Created' % item.ljust(40))
                cmds.menuItem(parent=self.main_menu, divider=True, dividerLabel=item.title())

                self._generate_menu(path, self.main_menu)

    def _generate_menu(self, dir_path, parent_menu):
        for root, dirs, files in os.walk(dir_path):
            dir_infos = list()

            for dir in dirs:
                with open(os.path.join(dir_path, dir, "_menu_info.json")) as f:
                    info = json.load(f)

                dir_infos.append([dir, info])

            dir_infos.sort(key=self.take_order)

            for dir_info in dir_infos:
                dir, info = dir_info

                if info["hidden"] is False:
                    en = info["enable"]
                    print ('\n\t%s|| Sub Menu Created' % dir.ljust(40))
                    new_parent_menu = cmds.menuItem(dir, parent=parent_menu, subMenu=True, label=dir.title(), en=en)

                    self._generate_menu(os.path.join(root, dir), new_parent_menu)

            for file in files:
                if file.endswith('.py') and not file.startswith("_"):
                    self._generate_button(os.path.join(root, file), parent_menu)

            return

    def _generate_button(self, file_path, parent_menu):
        file_base = os.path.basename(file_path).split(".py")[0]

        mod_list = os.path.dirname(file_path).split(os.path.dirname(self.root_path))[-1].split('\\')[2:]
        mod_list.append(file_base)
        mod_path = ".".join(mod_list)

        label = file_base.title().replace("_", " ")

        try:
            mod = __import__(mod_path, (), (), [file_base])
            reload(mod)

            en = True
            try:
                en = mod.enable
            except Exception as e:
                pass

            cmds.menuItem(parent=parent_menu, label=label, command=mod.main, en=en)
            print ('\t\t%s|| Success' % file_base.ljust(40))

        except Exception as e:
            print ('\t\t%s|| Failed : %s' % (file_base.ljust(40), e))
            pass
