from eden.autoRig.blueprints import singleGuideBP


def test_singleGuideBP():
    bp1 = singleGuideBP.SingleGuideBP("BP")
    bp1.build()

    assert bp1.guides == ["BP_guide"]
    assert bp1.handles == ["BP_guide"]
    assert bp1.prefix == "BP"
    assert bp1.topBlueprints == "blueprints"
