Sub Main
    Dim App as femap.model
    Set App = feFemap()

    Dim FePoint As femap.Point
    Set FePoint = App.fePoint

    Dim FeCurve As femap.Curve
    Set FeCurve = App.feCurve

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
    Dim FeSurfID As Long
    Dim FeCurveID As Long

    Dim FeCurveSet As femap.Set
    Set FeCurveSet = App.feSet

    Dim store(5) As Double

    rc = FeSurfaceSet.AddAll(FT_SURFACE)

    FeSurfaceSet.Reset
	FeSurfaceSet.First
    For i = 1 To FeSurfaceSet.Count
		FeSurfID = FeSurfaceSet.CurrentID
		rc = FeCurveSet.AddRule(FeSurfaceSet.CurrentID, FGD_CURVE_ONSURFACE)
		FeCurveSet.Reset
		FeCurveSet.First
		For j = 1 To FeCurveSet.Count
			FeCurveID = FeCurveSet.CurrentID
			store( (i-1)*3 + (j-1)) =FeCurveID
		FeCurveSet.Next
	    Next j
    	FeCurveSet.clear
		FeSurfaceSet.Next
    Next i

FeCurve.ID = store(2)
rc = SetToSweep.Add(FeCurve.ID)
FeCurve.ID = store(5)
rc = SetToSweep.Add(FeCurve.ID)

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
App.feAppMessage(FCM_NORMAL, Str$(SetToMesh.Count))

rc = App.feMeshSizeSurface(SetToMesh.ID, True, -0.125, 0, 0, 0, 0, 0, 1, 0, 0, False)
rc = App.feMeshSurface2(SetToMesh.ID, FeProp.ID, FTO_QUAD4, True, False)





















    
End Sub
