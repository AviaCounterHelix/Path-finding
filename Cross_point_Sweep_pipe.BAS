Sub Main
    Dim App as femap.model
    Set App = feFemap()

    Dim FePoint As femap.Point
    Set FePoint = App.fePoint

    Dim FeCurve As femap.Curve
    Set FeCurve = App.feCurve
    Dim FeCurveID As Long

    Dim diametr As Double

    Dim cx As Double
    Dim cy As Double
    Dim cz As Double

    Dim vecBase As Variant
	Dim vecDir As Variant
	Dim length As Double

	Dim SetToSweep As femap.Set
	Set SetToSweep = App.feSet

	Dim SetAlongSweep As femap.Set
	Set SetAlongSweep = App.feSet

	Dim SetAlongSweepID As Long

    rc = App.feVectorPick( "Select  Vector", False, length, vecBase, vecDir )
	rc = SetAlongSweep.AddAll(FT_CURVE)

    Dim x2 As Double
    Dim y2 As Double
    Dim z2 As Double

    x2 = length * vecDir(0) + vecBase(0)
    y2 = length * vecDir(1) + vecBase(1)
    z2 = length * vecDir(2) + vecBase(2)

	Dim dx As Double
    Dim dy As Double
    Dim dz As Double

    Dim wx As Double
    Dim wy As Double
    Dim wz As Double

    dx =x2 - vecBase(0)
    dy =y2 - vecBase(1)
    dz =z2 - vecBase(2)

    If dx <> 0 Or dy <> 0 Then
        wx = -dy
        wy = dx
        wz = 0.0
    Else
	    wx = 1.0
        wy = 0.0
        wz = 0.0
    End If

    norm = (wx^2 + wy^2 + wz^2)^0.5

    wx = wx / norm
    wy = wy / norm
    wz = wz / norm

    diametr = 30.0
    cx =vecBase(0) + diametr*wx / 2.0
    cy =vecBase(1) + diametr*wy / 2.0
    cz =vecBase(2) + diametr*wz / 2.0

    FePoint.x = cx
    FePoint.y = cy
    FePoint.z = cz

    rc = FePoint.Put(FePoint.NextEmptyID)

    Dim startPoint As femap.Point
    Set startPoint =App.fePoint

    startPoint.x = vecBase(0)
    startPoint.y = vecBase(1)
    startPoint.z = vecBase(2)
    startPoint.ID = startPoint.NextEmptyID
    startPoint.Put(startPoint.ID)

    FeCurve.type = FCU_LINE
    FeCurve.StdPoint(0) = startPoint.ID
    FeCurve.StdPoint(1) = FePoint.ID
    ID_curve =FeCurve.NextEmptyID
    FeCurve.Put(ID_curve)

    rc = App.feSurfaceRevolve(-FeCurve.ID, 360.0, vecBase, vecDir)

    Dim FeSurfaceSet As femap.Set
    Set FeSurfaceSet = App.feSet
    rc = FeSurfaceSet.AddAll(FT_SURFACE)

    Dim FeCurveSet As femap.Set
    Set FeCurveSet = App.feSet

    rc = FeCurveSet.AddAll(FT_CURVE)

    Dim center As Variant
    Dim normal As Variant
    Dim start As Variant
    Dim ends As Variant
    Dim angle As Double
    Dim radi As Double

    FeCurveSet.Reset
    FeCurveSet.First
    For i = 1 To FeCurveSet.Count
		angle = 0
		radi = 0
		FeCurveID = FeCurveSet.CurrentID
		FeCurve.Get(FeCurveID)
		FeCurve.ArcCircleInfo(center, normal, start, ends, angle, radi)
		If angle > 0 And radi > 0 Then
			SetToSweep.Add(FeCurve.ID)
		End If
		FeCurveSet.Next
    Next i

    rc = App.feSurfaceSweep(SetToSweep.ID, SetAlongSweep.ID)
    rc = App.feDelete(FT_SURFACE, FeSurfaceSet.ID)

    Dim FeMatl As femap.Matl
    Set FeMatl = App.feMatl

    FeMatl.type = FMT_ISOTROPIC
    FeMatl.title = "Steel"
    FeMatl.mval(0) = 21000
    FeMatl.mval(6) = 0.3
    FeMatl.Put(FeMatl.NextEmptyID)

    Dim FeProp As femap.Prop
    Set FeProp = App.feProp

    FeProp.type = FET_L_PLATE
    FeProp.title = "Tube thickness"
    FeProp.matlID = FeMatl.ID
    FeProp.pval(0) = 1
    FeProp.Put(FeProp.NextEmptyID)

    Dim SetToMesh As femap.Set
    Set SetToMesh = App.feSet

    SetToMesh.AddAll(FT_SURFACE)
    SetToMesh.Reset

    rc = App.feMeshSizeSurface(SetToMesh.ID, True, -0.125, 0, 0, 0, 0, 0, 1, 0, 0, False)
    rc = App.feMeshSurface2(SetToMesh.ID, FeProp.ID, FTO_QUAD4, True, False)

    Dim SetAllCurve As femap.Set
    Set SetAllCurve = App.feSet

    Dim SetArcCurve As femap.Set
    Set SetArcCurve = App.feSet

    rc = SetAllCurve.AddAll(FT_CURVE)
    SetAllCurve.Reset
    SetAllCurve.First

    For k = 1 To SetAllCurve.Count
    	FeCurveID = SetAllCurve.CurrentID
	    angle = 0
	    radi = 0
	    FeCurve.Get(FeCurveID)
        FeCurve.ArcCircleInfo(center, normal, start, ends, angle, radi)
        If angle > 0 And radi >0 Then
			        SetArcCurve.Add(FeCurve.ID)
        End If
        SetAllCurve.Next
    Next k

    SetArcCurve.Reset

    Dim SetNodebyCurve As femap.Set
    Set SetNodebyCurve = App.feSet

    SetArcCurve.First
    For i = 1 To SetArcCurve.Count
		FeCurveID = SetArcCurve.CurrentID
		rc = SetNodebyCurve.AddRule(FeCurveID, FGD_NODE_ATCURVE)
		SetArcCurve.Next
    	
    Next i

    SetNodebyCurve.Reset

    Dim bcs As femap.BCSet
	Set bcs = App.feBCSet

	bcs.title = "Fix"
	bcs.Put(bcs.NextEmptyID)
	bcs.Active = bcs.ID

	Dim bcn As femap.BCNode
	Set bcn = App.feBCNode
	 bcn.SetID = bcs.ID

	Dim ns As femap.Node
	Set ns = App.feNode

	Dim nodeID As Long

	SetNodebyCurve.First
	For i = 1 To SetNodebyCurve.Count
		nodeID = SetNodebyCurve.CurrentID
		ns.Get(nodeID)
		rc = bcn.Add(-ns.ID,True,True,True,True,True,True)
		
		SetNodebyCurve.Next
	Next i

	bcn.Put(bcn.NextEmptyID)

	Dim PressureLoad As Double
	PressureLoad = 2.33

	Dim SetFeElem As femap.Set
	Set SetFeElem = App.feSet
	rc = SetFeElem.AddAll(FT_ELEM)

	Dim FeElemID As Long

	Dim LS As femap.LoadSet
	Set LS = App.feLoadSet
	LS.title = "Pressure"
	LS.Put(LS.NextEmptyID)
	LS.Active = LS.ID

	Dim pressure As femap.LoadMesh
	Set pressure = App.feLoadMesh
	pressure.type = FLT_EPRESSURE
	pressure.CSys = 0
	pressure.LoadValue = PressureLoad
	pressure.FaceNumber = 1

	SetFeElem.Reset
	SetFeElem.First
	For i = 1 To SetFeElem.Count
		FeElemID = SetFeElem.CurrentID
		pressure.meshID = FeElemID
		pressure.Put (pressure.NextEmptyID)
		SetFeElem.Next
	Next i

	Dim am As femap.AnalysisMgr
    Set am = App.feAnalysisMgr

    Dim amID As Long
    amID = am.NextEmptyID()
    am.title = "Nonlinear Static Analysis"
    am.Solver = 36
    am.AnalysisType = 10

    am.NasBulkLangle = True

    Dim activeLoadSetID As Long
    Dim activeConstraintSetID As Long
    activeLoadSetID = 1
   activeConstraintSetID = 1

    am.BCSet(0) = activeConstraintSetID
    am.BCSet(2) = activeLoadSetID
	am.NasCnlOn = True
    am.NasCnlIncrements = 25
    am.NasCnlMaxIter = 50
    am.NasCnlConvergenceFlags(1) = True
    am.NasCnlConvergenceFlags(2) = True
    am.NasCnlConvergenceValue(1) = 0.001
    am.NasCnlConvergenceValue(2) = 1/10000000
    am.NasCnlStiffnessMethod = 1
    am.NasCnlKstep = 5
    am.NasCnlIntermediateOutput = 2

    am.Output(2) = -1
    am.Output(16) = -1
	am.CornerOutput = -1

    am.Put(amID)
    am.Analyze(amID)

End Sub
