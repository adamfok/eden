from eden.autoRig.blueprints import planarGuidesBP ; reload(planarGuidesBP)
cmds.file(new=True, force=True)
bp = planarGuidesBP.PlanarGuidesBP("BP", numGuides=4)
bp.build()