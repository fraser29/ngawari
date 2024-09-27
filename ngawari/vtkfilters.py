"""
@author Fraser Callaghan
"""


import vtk
from vtk.util import numpy_support # type: ignore
import numpy as np
from typing import List, Dict, Union, Optional, Tuple
from . import ftk

from ngawari._vtk_numpy_helpers import *

# ======================================================================================================================
#           VTK TYPE CHECKERS
# ======================================================================================================================
def isVTI(data):
    return data.IsA('vtkImageData')
def isVTP(data):
    try:
        return data.IsA('vtkPolyData')
    except AttributeError:
        return False


# ======================================================================================================================
#           VTK MATH
# ======================================================================================================================
def angleBetweenTwoVectors(vecA, vecB):
    return vtk.vtkMath.AngleBetweenVectors(vecA, vecB)


# ======================================================================================================================
#           VTK SOURCE
# ======================================================================================================================
def buildImplicitSphere(centerPt, radius):
    """ returns vtkSphere - for implicit functions etc
        use buildSphereSource if want polydata
    """
    vtksphere = vtk.vtkSphere()
    vtksphere.SetCenter(centerPt[0], centerPt[1], centerPt[2])
    vtksphere.SetRadius(radius)
    return vtksphere

def buildSphereSource(centerPt, radius, res=8):
    """ returns sphere polydata
    """
    vtksphere = vtk.vtkSphereSource()
    vtksphere.SetCenter(centerPt)
    vtksphere.SetRadius(radius)
    vtksphere.SetPhiResolution(res)
    vtksphere.SetThetaResolution(res)
    vtksphere.Update()
    return vtksphere.GetOutput()

def buildCylinderSource(centerPt, radius, height, res=8, norm=None):
    """ returns sphere polydata
    """
    vtkCyl = vtk.vtkCylinderSource()
    vtkCyl.SetCenter(centerPt)
    vtkCyl.SetRadius(radius)
    vtkCyl.SetHeight(height)
    vtkCyl.SetResolution(res)
    vtkCyl.Update()
    cyl = vtkCyl.GetOutput()
    if norm is not None:
        return translatePoly_AxisA_To_AxisB(cyl, [0,1,0], norm)
    return cyl

def buildImplicitBox(faceCP, norm, boxWidth, boxThick):
    """
    Builds a box so that the face cp is given and then a thick in the norm direction
    :param faceCP:
    :param norm:
    :param boxWidth:
    :param boxThick:
    :return:
    """
    norm = ftk.normaliseArray(norm)
    vtkBox = vtk.vtkBox()
    bW, bT = boxWidth / 2.0, boxThick / 2.0
    vtkBox.SetBounds(-bW, bW, -bW, bW, -bT, bT)
    aLabelTransform = vtk.vtkTransform()
    aLabelTransform.PostMultiply()
    aLabelTransform.Identity()
    rad = ftk.angleBetween2Vec(norm, [0, 0, 1])
    rotVec = np.cross(norm, [0, 0, 1])
    deg = ftk.rad2deg(rad)
    tt = np.array(faceCP) + np.array(norm) * bT
    aLabelTransform.RotateWXYZ(-deg, rotVec[0], rotVec[1], rotVec[2])
    aLabelTransform.Translate(tt[0], tt[1], tt[2])
    vtkBox.SetTransform(aLabelTransform)
    return vtkBox

def buildCubeSource(faceCP, norm, boxWidth, boxThick):
    cube = vtk.vtkCubeSource()
    bW, bT = boxWidth / 2.0, boxThick / 2.0
    cube.SetBounds(-bW, bW, -bW, bW, -bT, bT)
    cube.Update()
    aLabelTransform = vtk.vtkTransform()
    aLabelTransform.PostMultiply()
    aLabelTransform.Identity()
    rad = ftk.angleBetween2Vec(norm, [0, 0, 1])
    rotVec = np.cross(norm, [0, 0, 1])
    deg = ftk.rad2deg(rad)
    tt = np.array(faceCP) + np.array(norm) * bT
    aLabelTransform.RotateWXYZ(-deg, rotVec[0], rotVec[1], rotVec[2])
    aLabelTransform.Translate(tt[0], tt[1], tt[2])
    tpd = vtk.vtkTransformPolyDataFilter()
    tpd.SetInputData(cube.GetOutput())
    tpd.SetTransform(aLabelTransform)
    tpd.Update()
    return tpd.GetOutput()


def buildPolyLineBetweenTwoPoints(ptStart, ptEnd, nPts):
    """ build a poly line between start and end points, with nPts
    """
    ptStart = np.array(ptStart)
    vec = np.array(ptEnd) - ptStart
    vecM = np.linalg.norm(vec)
    vec_unit = vec / vecM
    dv = vecM / (nPts - 1)
    vPts = vtk.vtkPoints()
    polyLine = vtk.vtkPolyLine()
    vPts.InsertPoint(0, (ptStart[0], ptStart[1], ptStart[2]))
    polyLine.GetPointIds().InsertId(0, 0)
    for k in range(1, nPts):
        newP = ptStart + (k * dv * vec_unit)
        vPts.InsertPoint(k, (newP[0], newP[1], newP[2]))
        polyLine.GetPointIds().InsertId(k, k)
    cells = vtk.vtkCellArray()
    cells.InsertNextCell(polyLine)
    polyData = vtk.vtkPolyData()
    polyData.SetPoints(vPts)
    polyData.SetLines(cells)
    return polyData


def buildPolyTrianglesAtCp(pts, refVec=None, NORMALS_OUT=True, cp=None): # FIXME - to labels
    pts = ftk.ensurePtsNx3(pts)
    if refVec is not None:
        if pts.shape[0] > 3:
            isClockwise = ftk.isClosedPolygonClockwise(pts, refVec)
            if NORMALS_OUT:
                if isClockwise:
                    pts = pts[::-1]
            else:
                if not isClockwise:
                    pts = pts[::-1]
    if cp is None:
        cp = np.mean(pts, 0)
    nPts, _ = pts.shape
    points = vtk.vtkPoints()
    points.SetNumberOfPoints(nPts+1)
    triCellArray = vtk.vtkCellArray()
    polyData = vtk.vtkPolyData()
    for k in range(nPts):
        tri = vtk.vtkTriangle()
        tri.GetPointIds().SetId(0, k)
        id2 = k + 1
        if k == (nPts-1):
            id2 = 0
        tri.GetPointIds().SetId(1, id2)
        tri.GetPointIds().SetId(2, nPts)
        triCellArray.InsertNextCell(tri)
        # points.InsertNextPoint(pts[k])
        points.SetPoint(k, pts[k])
    # points.InsertNextPoint(cp)
    points.SetPoint(k+1, cp)
    polyData.SetPoints(points)
    polyData.SetPolys(triCellArray)
    return polyData


def _getOptimalPlaneSize_Resolution(data, subDivide=100):
    PLANE_SIZE = getMaximumBounds(data)
    RESOLUTION = PLANE_SIZE / subDivide
    return PLANE_SIZE, RESOLUTION


def buildPlaneCentredOnRoi(roiVTK, PLANE_SIZE=None, RESOLUTION=None, subDivide=100):
    if PLANE_SIZE is None:
        PLANE_SIZE, RESOLUTION = _getOptimalPlaneSize_Resolution(roiVTK, subDivide)
    pts = getVtkPointsAsNumpy(roiVTK)
    return buildPlaneCentredOnO(roiVTK.GetCenter(), pts[0], ftk.fitPlaneToPoints(pts)[:3], PLANE_SIZE, RESOLUTION)


def buildPlaneCentredOnSphere(sphereVTK, structVTK, vecArrayName='Velocity_m_per_s',
                              PLANE_SIZE=0.07, RESOLUTION=0.001):
    structPts = getVtkPointsAsNumpy(structVTK)
    cID = ftk.getIdOfPointClosestToX(sphereVTK.GetCenter(), structPts)
    norm = getArrayAsNumpy(structVTK, vecArrayName)[cID]
    return buildPlanePtAndNorm(sphereVTK.GetCenter(), norm, PLANE_SIZE, RESOLUTION)


def buildPlanePtAndNorm(X, norm, PLANE_SIZE=0.07, RESOLUTION=0.001):
    norm = ftk.normaliseArray(norm)
    cc = ftk.buildCircle3D(X, norm, PLANE_SIZE, 25)
    v1 = ftk.normaliseArray(cc[0] - X)
    v2 = np.cross(norm, v1)
    v3 = np.cross(norm, v2)
    nDiv = int(PLANE_SIZE / RESOLUTION)
    newPlane = buildPlaneSource(X, X + PLANE_SIZE * v2, X + PLANE_SIZE * v3, [nDiv, nDiv])
    return filterTransformPolyData(newPlane, disp=np.array(X) - np.array(newPlane.GetCenter()))


def buildPlaneCentredOnO(O, pointInplane, norm, PLANE_SIZE=0.07, RESOLUTION=0.001):
    v1 = ftk.normaliseArray(pointInplane - O)
    nDiv = int(PLANE_SIZE / RESOLUTION)
    v2 = np.cross(v1, norm)
    newPlane = buildPlaneSource(O, O + PLANE_SIZE * v1, O + PLANE_SIZE * v2, [nDiv, nDiv])
    return filterTransformPolyData(newPlane, disp=np.array(O) - np.array(newPlane.GetCenter()))


def buildPlaneSource(origin, pt1, pt2, nDivXY):
    plane = vtk.vtkPlaneSource()
    plane.SetOrigin(origin)
    plane.SetPoint1(pt1)
    plane.SetPoint2(pt2)
    plane.SetResolution(nDivXY[0], nDivXY[1])
    plane.Update()
    return plane.GetOutput()


def buildPolyLineFromXYZ_spline(xyz, splineDist, LOOP=False):
    pp = buildPolyLineFromXYZ(xyz, LOOP=LOOP)
    pp = filterVtpSpline(pp, splineDist)
    return pp


def buildPolyLineFromXYZ(xyz, LOOP=False):
    """ build a poly line
        - if LOOP - then close with extra lineseg between last and first points
    """
    vPts = vtk.vtkPoints()
    polyLine = vtk.vtkPolyLine()
    vPts.InsertPoint(0, (xyz[0][0], xyz[0][1], xyz[0][2]))
    polyLine.GetPointIds().InsertId(0, 0)
    for k in range(1, len(xyz)):
        vPts.InsertPoint(k, (xyz[k][0], xyz[k][1], xyz[k][2]))
        polyLine.GetPointIds().InsertId(k, k)
    if LOOP:
        polyLine.GetPointIds().InsertId(len(xyz), 0)
    cells = vtk.vtkCellArray()
    cells.InsertNextCell(polyLine)
    polyData = vtk.vtkPolyData()
    polyData.SetPoints(vPts)
    polyData.SetLines(cells)
    return polyData


def buildPolydataFromXYZ(xyz):
    xyz = ftk.__forcePts_nx3(xyz)
    myVtkPoints = vtk.vtkPoints()
    vertices = vtk.vtkCellArray()
    for k in range(xyz.shape[0]):
        try:
            ptID = myVtkPoints.InsertNextPoint(xyz[k, 0], xyz[k, 1], xyz[k, 2])
        except IndexError:
            break
        vertices.InsertNextCell(1)
        vertices.InsertCellPoint(ptID)
    polyData = vtk.vtkPolyData()
    polyData.SetPoints(myVtkPoints)
    polyData.SetVerts(vertices)
    return polyData


# ======================================================================================================================
#           CLIPPING & CUTTING
# ======================================================================================================================
def clippedByCircle(data, centerPt, normal, radius, COPY=False):
    data2 = getDataCutByPlane(data, normal, centerPt)
    pOut = getPolyDataClippedBySphere(data2, centerPt, radius)
    if COPY:
        return copyPolyData(pOut)
    return pOut


def getDataCutByPlane(data, normal, planePt):
    vtkplane = vtk.vtkPlane()
    vtkplane.SetOrigin(planePt[0], planePt[1], planePt[2])
    vtkplane.SetNormal(normal[0], normal[1], normal[2])
    vtkcutplane = vtk.vtkCutter()
    vtkcutplane.SetInputData(data)
    vtkcutplane.SetCutFunction(vtkplane)
    vtkcutplane.Update()
    return vtkcutplane.GetOutput()


def getPolyDataClippedByROI(data, roi, INSIDE=False, axialDisplacement=0.02,
                            closestPt=None, refNorm=None, boxWidth=None, boxWidthFactor=3.0): # FIXME
    """ If no closest point given will return largest.
        refNorm points into volume
    """
    try:
        R = getPolyDataMeanFromCenter(roi)
        X = roi.GetCenter()
    except AttributeError:
        X = roi
        R = 0.025
    try:
        len(refNorm)
        normT = ftk.fitPlaneToPoints(getPtsAsNumpy(roi))[:3]
        norm = ftk.setVecAConsitentWithVecB(normT, refNorm)
    except TypeError:
        norm = ftk.fitPlaneToPoints(getPtsAsNumpy(roi))[:3]
    if boxWidth is None:
        boxWidth = boxWidthFactor * R
    if closestPt is None:
        if refNorm is not None:
            closestPt = 'CP-NORM'
    return getPolyDataClippedByBox(data, X, norm, boxWidth, axialDisplacement,
                                   INSIDE=INSIDE, closestPt=closestPt)


def getPolyDataClippedByBox(data, cp, norm, boxWidth, boxThick, INSIDE=False,
                            closestPt=None, RETURN_FULL=False):
    """ Note - norm moves the box opposite so if inside then flip norm
        If no closest point given will return largest
        If closestPt == 'CP-NORM' then will use cp and norm and boxThick to calc closest pt
    """
    norm = ftk.normaliseArray(norm)
    vtkBox = vtk.vtkBox()
    bW, bT = boxWidth / 2.0, boxThick / 2.0
    vtkBox.SetBounds(-bW, bW, -bW, bW, -bT, bT)
    aLabelTransform = vtk.vtkTransform()
    aLabelTransform.Identity()
    rad = ftk.angleBetween2Vec(norm, [0, 0, 1])
    rotVec = np.cross(norm, [0, 0, 1])
    deg = ftk.rad2deg(rad)
    aLabelTransform.RotateWXYZ(deg, rotVec[0], rotVec[1], rotVec[2])
    tt = cp - norm * bT
    aLabelTransform.Translate(-tt[0], -tt[1], -tt[2])
    vtkBox.SetTransform(aLabelTransform)
    vtkcutbox = vtk.vtkClipPolyData()
    vtkcutbox.SetClipFunction(vtkBox)
    vtkcutbox.SetInputData(data)
    if INSIDE:
        vtkcutbox.InsideOutOn()
    vtkcutbox.Update()
    clipVol = vtkcutbox.GetOutput()
    if RETURN_FULL:
        return clipVol
    if (type(closestPt)==str) and (closestPt == 'CP-NORM'):
        closestPt = cp+(norm*3.0*bT)
    try:
        len(closestPt)
        # return getConnectedRegionClosestToX(clipVol, closestPt)
        return getConnectedRegionMinDistToX(clipVol, closestPt)
    except TypeError:
        return getConnectedRegionLargest(clipVol)


def getPolyDataClippedBySphere(data, centerPt, radius, CRINKLECLIP=False):
    vtksphere = buildImplicitSphere(centerPt, radius)
    if CRINKLECLIP:
        vtkcutsphere = vtk.vtkExtractGeometry()
    else:
        vtkcutsphere = vtk.vtkClipPolyData()
    vtkcutsphere.SetInputData(data)
    if CRINKLECLIP:
        vtkcutsphere.SetImplicitFunction(vtksphere)
        vtkcutsphere.ExtractInsideOn()
        vtkcutsphere.ExtractBoundaryCellsOn()
    else:
        vtkcutsphere.SetClipFunction(vtksphere)
        vtkcutsphere.InsideOutOn()
    vtkcutsphere.Update()
    return vtkcutsphere.GetOutput()


def clippedByPolyData(data, polyData):
    implicitPolyDataDistance = vtk.vtkImplicitPolyDataDistance()
    implicitPolyDataDistance.SetInput(polyData)
    #
    signedDistances = vtk.vtkFloatArray()
    signedDistances.SetNumberOfComponents(1)
    signedDistances.SetName("SignedDistances")
    # Evaluate the signed distance function at all of the grid points
    for pointId in range(data.GetNumberOfPoints()):
        p = data.GetPoint(pointId)
        signedDistance = implicitPolyDataDistance.EvaluateFunction(p)
        signedDistances.InsertNextValue(signedDistance)
    # add the SignedDistances to the grid
    data.GetPointData().SetScalars(signedDistances)
    # use vtkClipDataSet to slice the grid with the polydata
    clipper = vtk.vtkClipDataSet()
    clipper.SetInputData(data)
    clipper.InsideOutOn()
    clipper.SetValue(0.0)
    clipper.Update()
    return clipper.GetOutput()


def doesLinePierceTri(p0, p1, triCell):
    # Perform intersection.
    tol = 1e-7
    x = [0, 0, 0]  # Intersection.
    xp = [0, 0, 0]  # Parametric coordinates of intersection.
    t = vtk.mutable(0)  # Line position, 0 <= t <= 1.
    subId = vtk.mutable(0)  # subId? No idea what it is, usually not needed.
    hasIntersection = triCell.IntersectWithLine(p0, p1, tol, t, x, xp, subId)
    return hasIntersection, x


def doesLinePiercePolygon(p0, p1, polygon):
    nTris = polygon.GetNumberOfCells()
    for k2 in range(nTris):
        tf, x = doesLinePierceTri(p0, p1, polygon.GetCell(k2))
        if tf:
            return k2
    return None


def clippedByPlane(data, centrePt, planeNormal):
    return clipDataByPlane(data, centrePt, planeNormal)


def clipDataByPlane(data, centrePt, planeNormal):
    plane = vtk.vtkPlane()
    plane.SetOrigin(centrePt[0], centrePt[1], centrePt[2])
    plane.SetNormal(planeNormal[0], planeNormal[1], planeNormal[2])
    vtkcutplane = vtk.vtkClipDataSet()
    vtkcutplane.SetInputData(data)
    vtkcutplane.SetClipFunction(plane)
    vtkcutplane.GenerateClipScalarsOn()
    vtkcutplane.Update()
    return vtkcutplane.GetOutput()


def clippedByPlaneClosedSurface(data, centrePt, planeNormal):
    plane = vtk.vtkPlane()
    plane.SetOrigin(centrePt[0], centrePt[1], centrePt[2])
    plane.SetNormal(planeNormal[0], planeNormal[1], planeNormal[2])
    capPlanes = vtk.vtkPlaneCollection()
    capPlanes.AddItem(plane)
    clip = vtk.vtkClipClosedSurface()
    clip.SetClippingPlanes(capPlanes)
    clip.SetInputData(data)
    clip.GenerateFacesOn()
    clip.Update()
    return clip.GetOutput()


def clippedBySphere(data, centerPt, radius):
    vtksphere = buildImplicitSphere(centerPt, radius)
    vtkcutsphere = vtk.vtkClipDataSet()
    vtkcutsphere.SetInputData(data)
    vtkcutsphere.SetClipFunction(vtksphere)
    vtkcutsphere.InsideOutOn()
    vtkcutsphere.Update()
    return vtkcutsphere.GetOutput()


def clippedByScalar(data, arrayName, clipValue, INSIDE_OUT=False):
    vtkClipper = vtk.vtkClipDataSet()
    vtkClipper.SetInputData(data)
    vtkClipper.SetValue(clipValue)
    vtkClipper.SetInputArrayToProcess(0, 0, 0, 0, arrayName)
    if INSIDE_OUT:
        vtkClipper.InsideOutOn()
    vtkClipper.Update()
    return vtkClipper.GetOutput()


def clipVolumeToEightPolydataBoxes(data, RETURN_ptIDs):
    '''
    Clips same ordering as outline filter
    6-7
    4-5
    | |
    2-3
    0-1
    :param data:
    :param RETURN_ptIDs: much faster for downstream operations
    :return: 8 polydata surfs
    '''
    cp = data.GetCenter()
    d = 0.00
    if RETURN_ptIDs:
        addNpArray(data, np.arange(0, data.GetNumberOfPoints()), 'pIDs')
    halfPX = clipDataByPlane(data, [cp[0]+d,cp[1],cp[2]], [1, 0, 0])
    halfNX = clipDataByPlane(data, [cp[0]-d,cp[1],cp[2]], [-1, 0, 0])
    quartPXPY = clipDataByPlane(halfPX, [cp[0],cp[1]+d,cp[2]], [0, 1, 0])
    quartPXNY = clipDataByPlane(halfPX, [cp[0],cp[1]-d,cp[2]], [0, -1, 0])
    quartNXPY = clipDataByPlane(halfNX, [cp[0],cp[1]+d,cp[2]], [0, 1, 0])
    quartNXNY = clipDataByPlane(halfNX, [cp[0],cp[1]-d,cp[2]], [0, -1, 0])
    c0 = clipDataByPlane(quartNXNY, [cp[0],cp[1],cp[2]-d], [0, 0, -1])
    c1 = clipDataByPlane(quartPXNY, [cp[0],cp[1],cp[2]-d], [0,0,-1])
    c2 = clipDataByPlane(quartNXPY, [cp[0],cp[1],cp[2]-d], [0,0,-1])
    c3 = clipDataByPlane(quartPXPY, [cp[0],cp[1],cp[2]-d], [0,0,-1])
    c4 = clipDataByPlane(quartNXNY, [cp[0],cp[1],cp[2]+d], [0, 0,1])
    c5 = clipDataByPlane(quartPXNY, [cp[0],cp[1],cp[2]+d], [0,0,1])
    c6 = clipDataByPlane(quartNXPY, [cp[0],cp[1],cp[2]+d], [0,0,1])
    c7 = clipDataByPlane(quartPXPY, [cp[0],cp[1],cp[2]+d], [0,0,1])
    if RETURN_ptIDs:
        return [getArrayAsNumpy(i, "pIDs").astype(int) for i in [c0,c1,c2,c3,c4,c5,c6,c7]]
    else:
        vtpBoxes = [filterExtractSurface(i) for i in [c0,c1,c2,c3,c4,c5,c6,c7]]
        if data.IsA('vtkPolyData'):
            return vtpBoxes
        vtpBoxes = [decimateTris(filterTriangulate(i), 0.9) for i in vtpBoxes]
        return vtpBoxes




# ======================================================================================================================
#           IMAGE DATA
# ======================================================================================================================
def vtiToVts(data):
    sg = vtk.vtkImageDataToPointSet()
    sg.AddInputData(data)
    sg.Update()
    return sg.GetOutput()

def vtsToVti(dataVts):#, MAKE_ISOTROPIC=False):
    return filterResampleToImage(dataVts)


def getVtsOrigin(dataVts):
    return dataVts.GetPoints().GetPoint(0)


def getVtsResolution(dataVts):
    o,p1,p2,p3 = [0.0,0.0,0.0],[0.0,0.0,0.0],[0.0,0.0,0.0],[0.0,0.0,0.0]
    i0,i1,j0,j1,k0,k1 = dataVts.GetExtent()
    dataVts.GetPoint(i0,j0,k0, o)
    dataVts.GetPoint(i0+1,j0,k0, p1)
    dataVts.GetPoint(i0,j0+1,k0, p2)
    dataVts.GetPoint(i0,j0,k0+1, p3)
    di = abs(ftk.distTwoPoints(p1, o))
    dj = abs(ftk.distTwoPoints(p2, o))
    dk = abs(ftk.distTwoPoints(p3, o))
    return [di, dj, dk]

def getResolution_VTI(data):
    return data.GetSpacing()

def vtsToVtiDimensions(dataVts):#, FACTOR=1.0, MAKE_ISOTROPIC=False):
    ''' Will calulate the dimensions, and extent of a
        vti if it were to fit a given vts.
        FACTOR is scale factor on resolution (e.g. x2=coarser)
    '''
    # if not type(FACTOR)==list:
    #     FACTOR = [FACTOR, FACTOR, FACTOR]
    bounds = dataVts.GetBounds()
    bb = np.array(dataVts.GetBounds())
    deltas = [bb[1]-bb[0], bb[3]-bb[2], bb[5]-bb[4]]
    dims0 = dataVts.GetDimensions()
    res0 = getVtsResolution(dataVts)
    # DX = res0[0]*(dims0[0]-1)
    # DY = res0[1]*(dims0[1]-1)
    DZ = res0[2]*(dims0[2]-1)
    DDi = [abs(DZ-deltas[i]) for i in range(3)]
    SLICE_DIR = np.argmin(DDi)
    if SLICE_DIR == 0:
        res = [res0[2], res0[0], res0[1]]
    elif SLICE_DIR == 1:
        res = [res0[0], res0[2], res0[1]]
    elif SLICE_DIR == 2:
        res = [res0[0], res0[1], res0[2]]
    dims = [int(deltas[i]/res[i]) for i in range(3)]

    # res = [i * j for i,j in zip(res, FACTOR)]
    # if MAKE_ISOTROPIC:
    #     res = [min(res), min(res), min(res)]
    # dims = [int(((bounds[i] - bounds[i - 1]) / iRes)) for i, iRes in zip([1, 3, 5], res)]
    sides = [(bounds[i] - bounds[i - 1]) for i in [1, 3, 5]]
    return dims, sides, res, [bounds[0], bounds[2], bounds[4]]

def getDimsResOriginFromOutline(outline, res, pad):
    try:
        if len(res) == 3:
            di, dj, dk = res[0], res[1], res[2]
        else:
            di, dj, dk = res[0], res[0], res[0]
    except TypeError:
        di, dj, dk = res, res, res
    origin = outline.GetPoints().GetPoint(0)
    DI = ftk.distTwoPoints(outline.GetPoints().GetPoint(0), outline.GetPoints().GetPoint(1))
    DJ = ftk.distTwoPoints(outline.GetPoints().GetPoint(0), outline.GetPoints().GetPoint(2))
    DK = ftk.distTwoPoints(outline.GetPoints().GetPoint(0), outline.GetPoints().GetPoint(4))
    nR, nC, nK = int(DI/di)+1+pad, int(DJ/dj)+1+pad, int(DK/dk)+1+pad
    return [nR,nC,nK], [di,dj,dk], [i-j*pad/2 for i,j in zip(origin,[di,dj,dk])]

def buildRawImageDataFromPolyData(polyData, res, pad=1):
    return buildRawImageDataFromOutline(getOutline(polyData), res, pad)
def buildRawImageDataFromOutline(outline, res, pad=1):
    dd, rr, oo = getDimsResOriginFromOutline(outline, res, pad)
    img = buildRawImageData(dd, rr, oo)
    return img

def buildRawImageDataFromOutline_dims(outline, dims):
    origin = outline.GetPoints().GetPoint(0)
    DI = ftk.distTwoPoints(outline.GetPoints().GetPoint(0), outline.GetPoints().GetPoint(1))
    DJ = ftk.distTwoPoints(outline.GetPoints().GetPoint(0), outline.GetPoints().GetPoint(2))
    DK = ftk.distTwoPoints(outline.GetPoints().GetPoint(0), outline.GetPoints().GetPoint(4))
    di = DI / dims[0]
    dj = DJ / dims[1]
    dk = DK / dims[2]
    img = buildRawImageData(dims, [di, dj, dk], origin)
    return img

def duplicateImageData(imData):
    return buildRawImageData(imData.GetDimensions(),
                             imData.GetSpacing(), 
                             imData.GetOrigin())

def buildRawImageData(dims, res, origin=[0 ,0 ,0]):
    newImg = vtk.vtkImageData()
    newImg.SetSpacing(res[0] ,res[1] ,res[2])
    newImg.SetOrigin(origin[0], origin[1], origin[2])
    newImg.SetDimensions(dims[0] ,dims[1] ,dims[2])
    return newImg

def surf2ImageBW(dataSurf, arrayName, res, nDilate=0, nMed=0):
    imBW = buildRawImageDataFromOutline(getOutline(dataSurf), res, pad=10)
    IDs = filterGetEnclosedPts(imBW, dataSurf, 'ID')
    inside = np.zeros(imBW.GetNumberOfPoints())
    inside[IDs] = 1.0
    addNpArray(imBW, inside, arrayName, SET_SCALAR=True)
    # dilate
    if nDilate > 0:
        for _ in range(nDilate):
            imBW = filterDilateErode(imBW, [3,3,3], valDilate=1, valErode=0)
    if nMed > 1:
        imBW = filterVtiMedian(imBW, nMed)
    return imBW

def getVarValueAtI_ImageData(imData, X, arrayName):
    """
    Useful to get the vel value at a location from imdata
    :param imData:
    :param X:
    :param arrayName:
    :return: tuple
    """
    iXID = imData.FindPoint(X)
    n = imData.GetPointData().GetArray(arrayName).GetTuple(iXID)
    return n

def getImageX(data, pointID):
    return data.GetPoint(pointID)

def imageX_ToStructuredCoords(imageData, xyz_list):
    """
    Note - this is no good if extracted a VOI from image already
    in this :

        id2 = ii.FindPoint(xyz)
        ijk = vtkfilters.imageIndex_ToStructuredCoords(ii, [id2])
    """
    # return a list of ijk
    ijk_list = []
    for iX in xyz_list:
        ijk = [0, 0, 0]
        pcoords = [0.0, 0.0, 0.0]
        res = imageData.ComputeStructuredCoordinates(iX, ijk, pcoords)
        if res == 0:
            continue
        ijk_list.append(ijk)
    return ijk_list

def imageIndex_ToStructuredCoords(imageData, index_list):
    dd = imageData.GetDimensions()
    return [np.unravel_index(i, shape=dd, order='F') for i in index_list]

def getNeighbours26_fromImageIndex(imageData, index, delta=1, RETURN_STRUCTCOORDS=False):
    dims = imageData.GetDimensions()
    strucCoord = imageIndex_ToStructuredCoords(imageData, [index])[0]
    newStructCoords = []
    for k0 in range(0-delta, 1+delta):
        for k1 in range(0-delta, 1+delta):
            for k2 in range(0-delta, 1+delta):
                newIjk = (strucCoord[0] + k0, strucCoord[1] + k1, strucCoord[2] + k2)
                if (min(newIjk)<0) or (newIjk[0]>=dims[0]) or (newIjk[1]>=dims[1]) or (newIjk[2]>=dims[2]):
                    continue
                if newIjk == strucCoord:
                    continue
                newStructCoords.append(newIjk)
    if RETURN_STRUCTCOORDS:
        return newStructCoords
    return imageStrucCoords_toIndex(imageData, newStructCoords)

def imageStrucCoords_toIndex(imageData, strucCoords_list):
    # dd = imageData.GetDimensions()
    # a =  [np.ravel_multi_index(i, dd, order='F') for i in strucCoords_list]
    b = [imageData.ComputePointId(ijk) for ijk in strucCoords_list]
    return b

def imageStrucCoords_toX(imageData, strucCoords_list):
    # Be awre - this is not considering any transform
    return [getImageX(imageData, i) for i in imageStrucCoords_toIndex(imageData, strucCoords_list)]



# ======================================================================================================================
#           POLY DATA
# ======================================================================================================================
def getPolyDataMeanFromCenter(data):
    return np.mean(ftk.distPointPoints(data.GetCenter(), getPtsAsNumpy(data)))



# ======================================================================================================================
#           COPY DATA
# ======================================================================================================================
def copyPolyData(data):
    dataOut = vtk.vtkPolyData()
    dataOut.DeepCopy(data)
    return dataOut


def copyData(data):
    if data.IsA('vtkImageData'):
        dataOut = vtk.vtkImageData()
    elif data.IsA('vtkPolyData'):
        dataOut = vtk.vtkPolyData()
    elif data.IsA('vtkUnstructuredGrid'):
        dataOut = vtk.vtkUnstructuredGrid()
    dataOut.DeepCopy(data)
    return dataOut



# ======================================================================================================================
#           VTK FILTERS
# ======================================================================================================================
def contourFilter(data: vtk.vtkDataObject, isoValue: float) -> vtk.vtkPolyData:
    """
    Find the triangles that lie along the 'isoValue' contour.

    Args:
        data (vtk.vtkDataObject): The VTK data object.
        isoValue (float): The iso value.

    Returns:
        vtk.vtkPolyData: The filtered data.
    """
    cF = vtk.vtkContourFilter()
    cF.SetInputData(data)
    cF.SetValue(0, isoValue)
    cF.Update()
    return cF.GetOutput()


def cleanData(data: vtk.vtkDataObject, tolerance: float = 0.0, DO_POINT_MERGING: bool = True) -> vtk.vtkPolyData:
    """ Cleans PolyData - merge points, remove pts not in cell, remove cells
        with no points etc.
        30.9.14: Set default tol=0.0, should be faster merging as no look up
                 of every pt. See class docs
    """
    cleaner = vtk.vtkCleanPolyData()
    cleaner.SetInputData(data)
    cleaner.SetAbsoluteTolerance(tolerance)
    cleaner.SetToleranceIsAbsolute(1)
    if not DO_POINT_MERGING:
        cleaner.PointMergingOff()
    cleaner.Update()
    return cleaner.GetOutput()


def filterVtpSpline(data, spacing=0.001, nPoints=None, smoothFactor=None):
    p0, pE = data.GetPoints().GetPoint(0), data.GetPoints().GetPoint(data.GetNumberOfPoints() - 1)
    if smoothFactor is not None:
        data = filterVtpSpline(data, nPoints=int(data.GetNumberOfPoints() / float(smoothFactor)))
    sf = vtk.vtkSplineFilter()
    sf.SetInputData(data)
    if nPoints is not None:
        sf.SetNumberOfSubdivisions(nPoints)
        spacing = ftk.distTwoPoints(p0, pE) / nPoints
    else:
        sf.SetSubdivideToLength()
        sf.SetLength(spacing)
    sf.Update()
    cl1 = sf.GetOutput()
    cl1 = cleanData(cl1, 0.05 * spacing)
    d0 = ftk.distTwoPoints(p0, cl1.GetPoints().GetPoint(0))
    d1 = ftk.distTwoPoints(p0, cl1.GetPoints().GetPoint(cl1.GetNumberOfPoints() - 1))
    if d1 < d0:
        xyz = getPtsAsNumpy(cl1)
        cl1 = buildPolyLineFromXYZ(xyz[::-1])
    return cl1


def filterTransformPolyData(polyData, scale=[1.0, 1.0, 1.0], disp=[0.0, 0.0, 0.0], rotate=None, matrix=None, rotateXYZ=None):
    transP = vtk.vtkTransform()
    if matrix:
        try:
            transP.SetMatrix(matrix)
        except TypeError:
            transP = matrix
    else:
        transP.Translate(disp[0], disp[1], disp[2])
        try:
            transP.Scale(scale[0], scale[1], scale[2])
        except TypeError:
            transP.Scale(scale, scale, scale)
        if rotate is not None:
            transP.RotateWXYZ(rotate[0], rotate[1], rotate[2], rotate[3])
        elif rotateXYZ is not None:
            transP.RotateX(rotateXYZ[0])
            transP.RotateY(rotateXYZ[1])
            transP.RotateZ(rotateXYZ[2])
    tpd = vtk.vtkTransformPolyDataFilter()
    tpd.SetInputData(polyData)
    tpd.SetTransform(transP)
    tpd.Update()
    return tpd.GetOutput()


def translatePoly_AxisA_To_AxisB(polyData, vecA, vecB):
    try:
        a1 = ftk.angleBetween2Vec(vecB, vecA)
    except TypeError:
        return polyData # vecA and vecB are basically aligned
    Rvec = np.cross(vecB, vecA)
    rotate = [-1 * ftk.rad2deg(a1), Rvec[0], Rvec[1], Rvec[2]]
    data0 = filterTransformPolyData(polyData, disp=[-1.0 * i for i in polyData.GetCenter()])
    data0R = filterTransformPolyData(data0, rotate=rotate)
    return filterTransformPolyData(data0R, disp=polyData.GetCenter())


def getOutline(dataIn):
    of = vtk.vtkOutlineFilter()
    of.SetInputData(dataIn)
    of.Update()
    return of.GetOutput()


def getMaximumBounds(data):
    oo = getOutline(data)
    dd = 0
    pts = getPtsAsNumpy(oo)
    for k1 in range(len(pts)):
        for k2 in range(k1+1, len(pts)):
            dx = ftk.distTwoPoints(pts[k1], pts[k2])
            if dx > dd:
                dd = dx
    return dd


def appendPolyData(data1, data2):
    appendFilter = vtk.vtkAppendPolyData()
    appendFilter.AddInputData(data1)
    # appendFilter.SetInputData(data1)
    appendFilter.AddInputData(data2)
    # appendFilter.SetInputData(data2)
    appendFilter.Update()
    return appendFilter.GetOutput()


def appendPolyDataList(dataList):
    if len(dataList) == 1:
        return dataList[0]
    appendFilter = vtk.vtkAppendPolyData()
    for iData in dataList:
        appendFilter.AddInputData(iData)
    appendFilter.Update()
    return appendFilter.GetOutput()


def appendImageList(image_list, appendAxis):
    """Combines images into one ."""
    append_filter = vtk.vtkImageAppend()
    append_filter.SetAppendAxis(appendAxis)  
    for iImage in image_list:
        append_filter.AddInputData(iImage)
    append_filter.Update()
    return append_filter.GetOutput()


def appendUnstructured(dataList):
    appendFilter = vtk.vtkAppendFilter()
    for iData in dataList:
        appendFilter.AddInputData(iData)
    appendFilter.Update()
    return appendFilter.GetOutput()


def mergeTwoImageData(ii1, ii2, newRes, arrayName):
    oo12 = appendPolyData(getOutline(ii1), getOutline(ii2))
    oC = getOutline(oo12)
    iiC = buildRawImageDataFromOutline(oC, newRes)
    A1 = getArrayAsNumpy(filterResampleToDataset(ii1, iiC), arrayName)
    A2 = getArrayAsNumpy(filterResampleToDataset(ii2, iiC), arrayName)
    AA = A1 + A2 / 2.0
    addNpArray(iiC, AA, arrayName, SET_SCALAR=True)
    return iiC


def multiblockToList(data):
    listOut = []
    for k1 in range(data.GetNumberOfBlocks()):
        pd = data.GetBlock(k1)
        listOut.append(pd)
    return listOut


def idListToVtkIDs(idsList):
    ids = vtk.vtkIdList()
    for i in idsList:
        ids.InsertNextId(i)
    return ids


def extractCells(data, vtkCellIds):
    """ returns unstructuredgrid of output cells """
    if type(vtkCellIds) == list:
        vtkCellIds = idListToVtkIDs(vtkCellIds)
    exCells = vtk.vtkExtractCells()
    exCells.SetInputData(data)
    exCells.SetCellList(vtkCellIds)
    exCells.Update()
    return exCells.GetOutput()


def extractSelection(data, vtkSelection):
    """ Data = vtu, vtkSelection made from vtkSelectionNode, vtkSelection
    """
    extractSelection = vtk.vtkExtractSelection()
    extractSelection.SetInputData(0, data)
    extractSelection.SetInputData(1, vtkSelection)
    extractSelection.Update()
    return extractSelection.GetOutput()


def delCellsByEdgeLength(data, edgeLength):
    """ Delete cells with edges greater than edgeLength
        Returns unstructuredGrid
    """
    allIds = list(range(data.GetNumberOfCells()))
    for k0 in range(data.GetNumberOfCells()):
        for k1 in range(data.GetCell(k0).GetNumberOfEdges()):
            p0 = data.GetCell(k0).GetEdge(k1).GetPoints().GetPoint(0)
            p1 = data.GetCell(k0).GetEdge(k1).GetPoints().GetPoint(1)
            if ftk.distTwoPoints(p0, p1) > edgeLength:
                allIds.remove(k0)
                break
    #
    ids = vtk.vtkIdList()
    for i in allIds:
        ids.InsertNextId(i)
    return extractCells(data, ids)


def delCellsByID(data, IDsToDEL):
    """ Delete cells from list of IDs
        Returns unstructuredGrid
    """
    allIds = list(range(data.GetNumberOfCells()))
    for delID in IDsToDEL:
        allIds.remove(delID)
    # have IDs to keep
    ids = vtk.vtkIdList()
    for i in allIds:
        ids.InsertNextId(i)
    return extractCells(data, ids)


def getPolylineLength(data):
    return ftk.cumulativeDistanceAlongLine(getPtsAsNumpy(data))[-1]


def getLoopSubDivided(data, nLoops):
    loopSubDiv = vtk.vtkLoopSubdivisionFilter()
    loopSubDiv.SetInputData(data)
    loopSubDiv.SetNumberOfSubdivisions(nLoops)
    loopSubDiv.Update()
    return loopSubDiv.GetOutput()


def decimateTris(data, factor):
    dF = vtk.vtkDecimatePro()
    dF.SetInputData(data)
    dF.SetTargetReduction(factor)
    dF.Update()
    return dF.GetOutput()


def shrinkWrapData(data, wrappingData=None, DEFAULT_WRAP_RES=100):
    """

    :param data:
    :param wrappingData: if None - then just make a sphere larger
    :return: wrapped data
    """
    sw = vtk.vtkSmoothPolyDataFilter()
    if wrappingData is None:
        X = data.GetCenter()
        R = np.max(ftk.distPointPoints(X, getPtsAsNumpy(data)))
        wrappingData = buildSphereSource(X, R*2.0, DEFAULT_WRAP_RES)
    sw.SetSourceData(data)
    sw.SetInputData(wrappingData)
    sw.Update()
    return sw.GetOutput()


def poissonRecon(data, depth=9):
    surface = vtk.vtkPoissonReconstruction()
    surface.SetDepth(depth);

    sampleSize = data.GetNumberOfPoints() * .00005
    if (sampleSize < 10):
        sampleSize = 10
    if (data.GetPointData().GetNormals()):
        surface.SetInputData(data)
    else:
        #  "Estimating normals using PCANormalEstimation" 
        normals = vtk.vtkPCANormalEstimation()
        normals.SetInputData(data)
        normals.SetSampleSize(sampleSize)
        normals.SetNormalOrientationToGraphTraversal()
        normals.FlipNormalsOff()
        surface.SetInputConnection(normals.GetOutputPort())
    surface.Update()
    return surface.GetOutput()


def pointCloudRemoveOutliers(data):
    locator = vtk.vtkStaticPointLocator()
    locator.SetDataSet(data)
    locator.BuildLocator()
    removal = vtk.vtkStatisticalOutlierRemoval()
    removal.SetInputData(data)
    removal.SetLocator(locator)
    removal.SetSampleSize(20)
    removal.SetStandardDeviationFactor(1.5)
    removal.GenerateOutliersOn()
    removal.Update()
    pp = removal.GetOutput()
    return buildPolydataFromXYZ(getPtsAsNumpy(pp))

def smoothTris(data, iterations=200):
    sF = vtk.vtkSmoothPolyDataFilter()
    sF.SetInputData(data)
    sF.SetNumberOfIterations(iterations)
    sF.Update()
    return sF.GetOutput()

def smoothTris_SINC(data, iterations=20):
    pass_band = 0.001
    feature_angle = 60.0
    smoother = vtk.vtkWindowedSincPolyDataFilter()
    smoother.SetInputData(data)
    smoother.SetNumberOfIterations(iterations)
    smoother.BoundarySmoothingOff()
    smoother.FeatureEdgeSmoothingOff()
    smoother.SetFeatureAngle(feature_angle)
    smoother.SetPassBand(pass_band)
    smoother.NonManifoldSmoothingOn()
    smoother.NormalizeCoordinatesOff()
    smoother.Update()
    return smoother.GetOutput()

def isPolyDataWaterTight(data):
    alg = vtk.vtkFeatureEdges()
    alg.FeatureEdgesOff()
    alg.BoundaryEdgesOn()
    alg.NonManifoldEdgesOff()
    alg.SetInputDataObject(data)
    alg.Update()
    is_water_tight = alg.GetOutput().GetNumberOfCells() < 1
    return is_water_tight

def isPolyDataPolyLine(data):
    for k1 in range(data.GetNumberOfCells()):
        aa = data.GetCell(k1).IsA('vtkPolyLine')
        # print(k1, aa) # DEBUG - WORKS
        if not aa:
            return False # if find any non-line - return false
    return True


def calculatePolyDataArea(vtpdata):  # latest version will allow compute on polydata
    nCells = vtpdata.GetNumberOfCells()
    A = 0.0
    for k1 in range(nCells):
        try:
            A += vtpdata.GetCell(k1).ComputeArea()
        except AttributeError:
            # This deals with case of polyline representing the ROI
            return calculatePolyDataArea(buildPolyTrianglesAtCp(getPtsAsNumpy(vtpdata)))
    return A

def getPolyDataCenterPtNormal(data, refNorm=None):
    """ return 2x np array center point, normal for each tri in poly data
    """
    # return flow norm -- mult by dens for mass flow
    nCells = data.GetNumberOfCells()
    cp, norm = [], []
    for k1 in range(nCells):
        iCell = data.GetCell(k1)
        centerPt, normal = __getTriangleCenterAndNormal(iCell)
        cp.append(centerPt)
        if refNorm is not None:
            normal = ftk.setVecAConsitentWithVecB(np.array(normal), refNorm)
        norm.append(normal)
    return np.array(cp), np.array(norm)

def addMagnitudeArray(data, vecArrayName, vecArrayNameOut):
    magA = np.sqrt(np.sum(np.power(getArrayAsNumpy(data, vecArrayName), 2.0), axis=-1))
    addNpArray(data, magA, vecArrayNameOut)


def addNormalVelocities(data, normal, vecArrayName, vecArrayNameOut):
    """ Will add scalar array of normal velocity magnitude
        output array: fDC.varNameVelocityNormal
    """
    normal = normal / np.linalg.norm(normal)
    velArray = getArrayAsNumpy(data, vecArrayName)
    vN = np.dot(velArray, normal)
    addNpArray(data, vN, vecArrayNameOut)
    return data



def filterDilateErode(imData, kernal, valDilate, valErode):
    # if binary then for dilate set valDilate=1, valErode=0
    #                for erode  set valDilate=0, valErode=1
    try:
        len(kernal)
    except TypeError:
        kernal = [kernal,kernal,kernal]
    dilateErode = vtk.vtkImageDilateErode3D()
    dilateErode.SetInputData(imData)
    dilateErode.SetDilateValue(valDilate)
    dilateErode.SetErodeValue(valErode)
    dilateErode.SetKernelSize(kernal[0], kernal[1], kernal[2])
    dilateErode.Update()
    return dilateErode.GetOutput()




def filterExtractSurface(data):
    geometryFilter = vtk.vtkGeometryFilter()
    geometryFilter.SetInputData(data)
    geometryFilter.Update()
    return geometryFilter.GetOutput()


def filterExtractTri(data):
    ss = filterExtractSurface(data)
    return filterTriangulate(ss)


def filterTriangulate(data):
    triFilter = vtk.vtkTriangleFilter()
    triFilter.SetInputData(data)
    triFilter.Update()
    return triFilter.GetOutput()




# ======================================================================================================================
#           TRIANGLE AREA & NORMAL
# ======================================================================================================================
def getTriangleAreaAndNormal(triCell):
    # return area_float, normal_float3
    cellPts = triCell.GetPoints()
    area = triCell.ComputeArea()
    normal = [0, 0, 0]
    triCell.ComputeNormal(cellPts.GetPoint(0), cellPts.GetPoint(1), cellPts.GetPoint(2), normal)
    return (area, normal)


def __getTriangleCenterAndNormal(triCell):
    # return area_float, normal_float3
    cellPts = triCell.GetPoints()
    # cp = triCell.GetCenter()
    cp = np.mean((cellPts.GetPoint(0), cellPts.GetPoint(1), cellPts.GetPoint(2)), 0)
    normal = [0, 0, 0]
    triCell.ComputeNormal(cellPts.GetPoint(0), cellPts.GetPoint(1), cellPts.GetPoint(2), normal)  # this is mag 1.0
    return (cp, normal)


# ======================================================================================================================
#           EDGES
# ======================================================================================================================
def getBoundaryEdges(data):
    fef = vtk.vtkFeatureEdges()
    fef.SetInputData(data)
    fef.BoundaryEdgesOn()
    fef.ManifoldEdgesOff()
    fef.NonManifoldEdgesOff()
    fef.FeatureEdgesOff()
    fef.Update()
    return fef.GetOutput()


def getEdges(data, FEATURE=False):
    fef = vtk.vtkFeatureEdges()
    fef.SetInputData(data)
    fef.BoundaryEdgesOn()
    fef.ManifoldEdgesOn()
    fef.NonManifoldEdgesOn()
    if FEATURE:
        fef.FeatureEdgesOn()
    else:
        fef.FeatureEdgesOff()
    fef.Update()
    return fef.GetOutput()


def getConnectedCellIds(dataMesh, searchId):
    connectedCells = vtk.vtkIdList()
    dataMesh.BuildLinks()
    dataMesh.GetPointCells(searchId, connectedCells)
    return connectedCells


def extractStructuredSubGrid(data, ijkMinMax=None, sampleRate=(1, 1, 1), TO_INCLUDE_BOUNDARY=False):
    if type(sampleRate) == int:
        sampleRate = (sampleRate, sampleRate, sampleRate)
    if ijkMinMax is None:
        ijkMinMax = data.GetExtent()
    if isinstance(data, vtk.vtkImageData):
        return extractVOI(data, ijkMinMax, sampleRate=sampleRate)
    extractGrid = vtk.vtkExtractGrid()
    extractGrid.SetInputData(data)
    extractGrid.SetVOI(ijkMinMax[0], ijkMinMax[1], ijkMinMax[2], ijkMinMax[3],
                       ijkMinMax[4], ijkMinMax[5])
    extractGrid.SetSampleRate(sampleRate[0], sampleRate[1], sampleRate[2])
    if TO_INCLUDE_BOUNDARY:
        extractGrid.IncludeBoundaryOn()
    extractGrid.Update()
    return extractGrid.GetOutput()


def extractVOI(data, ijkMinMax, sampleRate=(1, 1, 1)):
    extractGrid = vtk.vtkExtractVOI()
    extractGrid.SetInputData(data)
    extractGrid.SetVOI(ijkMinMax[0], ijkMinMax[1], ijkMinMax[2], ijkMinMax[3],
                       ijkMinMax[4], ijkMinMax[5])
    extractGrid.SetSampleRate(sampleRate[0], sampleRate[1], sampleRate[2])
    # extractGrid.IncludeBoundaryOn()
    extractGrid.Update()
    return extractGrid.GetOutput()


def extractVOI_fromFov(data, fovData):
    bounds = fovData.GetBounds()
    bb = []
    for k1 in [0, 1]:
        for k2 in [2, 3]:
            for k3 in [4, 5]:
                pt = [bounds[k1], bounds[k2], bounds[k3]]
                bb.append(pt)
    ti, tj, tk = [999990, 0], [999990, 0], [999990, 0]
    for X in bb:
        ijk = [0, 0, 0]
        pp = [0, 0, 0]
        oo = data.ComputeStructuredCoordinates(X, ijk, pp)
        for k0, tt in zip(ijk, [ti, tj, tk]):
            tt[0] = min(tt[0], k0)
            tt[1] = max(tt[1], k0)
    tijk = [ti[0], ti[1], tj[0], tj[1], tk[0], tk[1]]
    return extractVOI(data, tijk)







def filterResampleToDataset(src, destData, PASS_POINTS=False):
    """
    Resample data from src onto destData
    :param src: source vtkObj
    :param destData: destination vtkObj
    :param PASS_POINTS: bool [False] set true to pass point data to output
    :return: destData with interpolated point data from src
    """
    pf = vtk.vtkProbeFilter()
    pf.SetInputData(destData)
    pf.SetSourceData(src)
    if PASS_POINTS:
        pf.PassPointArraysOn()
    pf.Update()
    return pf.GetOutput()

def filterResampleDictToDataset(srcDict, destData):
    """
    Run filterResampleToDataset for every src in srcDict to static destData
    :param srcDict: dictionary of timekey: vtkObj
    :param destData: destination vtkObj - static
    :return: dictionary of timeKey:destVtkObj with src point data
    """
    dictOut = {}
    for iK in srcDict.keys():
        dictOut[iK] = filterResampleToDataset(srcDict[iK], destData)
    return dictOut

def filterResampleToImage(vtsObj, dims=None, bounder=None):
    rif = vtk.vtkResampleToImage()
    rif.SetInputDataObject(vtsObj)
    if dims is None:
        dims = [0,0,0]
        vtsObj.GetDimensions(dims)
    try:
        _ = dims[0]
    except TypeError:
        dims = [dims, dims, dims]
    if bounder is not None:
        rif.UseInputBoundsOff()
        rif.SetSamplingBounds(bounder.GetBounds())
    rif.SetSamplingDimensions(dims[0],dims[1],dims[2])
    rif.Update()
    return rif.GetOutput()







def filterResliceImage(vtiObj, X, normalVector, guidingVector=None,
                       slabNumberOfSlices=1,
                       LINEAR_INTERPOLATION=False, MIP=False,
                       OUTPUT_DIM=2):
    """
    This returns a reslice
        add .GetOutput() to get the slice as imagedata
    EXAMPLE:
            ii = vtkfilters.filterResliceImage(vtiObj, X, n, [0,0,1])
            iI = ii.GetOutput()
            axT = ii.GetResliceAxes()
            c = contourFilter(iI, 450)
            c = filterTransformPolyData(c, matrix=axT)
    :param vtiObj: vtiObject to reslice
    :param X: loaction of slice center
    :param normalVector: normal vector defining slice
    :param guidingVector: 3_tuple - inplane vector to define slice x-axis [default None - will choose]
    :param slabNumberOfSlices: int - to make a thick slice [default=1]
    :param LINEAR_INTERPOLATION: bool - set true to have linear interpolation [default cubic]
    :param MIP: bool - set true for thick slice to show MIP [default mean]
    :param OUTPUT_DIM: int - set 3 for volume [default 2]
    :return: vtk.vtkImageReslice object
    """
    reslice = vtk.vtkImageReslice()
    reslice.SetInputData(vtiObj)
    reslice.SetOutputDimensionality(OUTPUT_DIM)
    if OUTPUT_DIM == 3:
        ss = vtiObj.GetSpacing()
        reslice.SetOutputSpacing(ss[0], ss[1], ss[2]*slabNumberOfSlices)
        reslice.SetSlabSliceSpacingFraction(1.0/slabNumberOfSlices)
    reslice.AutoCropOutputOn()
    u, v, normalVector = getAxesDirectionCosinesForNormal(normalVector, guidingVector)
    reslice.SetResliceAxesDirectionCosines(u, v, normalVector)
    reslice.SetResliceAxesOrigin(X)
    if LINEAR_INTERPOLATION:
        reslice.SetInterpolationModeToLinear()
    else:
        reslice.SetInterpolationModeToCubic()
    reslice.SetSlabNumberOfSlices(slabNumberOfSlices)
    if MIP:
        reslice.SetSlabModeToMax() # default is mean
    reslice.Update()
    return reslice

def filterVtiMedian(vtiObj, filterKernalSize=3):
    mf = vtk.vtkImageMedian3D()
    mf.SetInputData(vtiObj)
    mf.SetKernelSize(filterKernalSize,filterKernalSize,filterKernalSize)
    mf.Update()
    return mf.GetOutput()

# def anisotropicDiffusion(vtiObj):
#     filtAD = vtk.vtkImageAnisotropicDiffusion3D()
#     filtAD.SetInputData(vtiObj)
#     filtAD.CornersOn()
#     filtAD.SetNumberOfIterations(5)
#     filtAD.SetDiffusionFactor(0.10)
#     filtAD.SetDiffusionThreshold(10)
#     filtAD.Update()
#     return filtAD.GetOutput()

def filterGetPointsInsideSurface(data, surfaceData):
    """
    classify points as inside(t) or outside(f)
    see filterNullOutsideSurface to use
    :param data: vtkObj
    :param surfaceData: closed polydata
    :return: list of true=INSIDE false=OUTSIDE
    """
    return filterGetEnclosedPts(data, surfaceData, 'tf')
def filterGetPointIDsInsideSurface(vtkObj, surf3D):
    return filterGetEnclosedPts(vtkObj, surf3D, 'ID')
def filterGetPolydataInsideSurface(vtkObj, surf3D):
    return filterGetEnclosedPts(vtkObj, surf3D, 'POLYDATA')
def filterGetEnclosedPts(vtkObj, surf3D, RETURNTYPE="POLYDATA", tol=0.0000000001):
    """
    Get all pts from vtkObj enclosed by surface.
    :param vtkObj: A vtkObj
    :param surf3D: A closed polydata surface
    :param RETURNTYPE: string - Options: 'POLYDATA' | 'tf' | 'ID'
    :param tol: default [0.00001]
    :return: polydata of points | np.array of true/false | list of IDs
    """
    try:
        tol = np.min(vtkObj.GetSpacing()) * 0.0001
    except AttributeError:
        tol=tol
    enclosedPts = vtk.vtkSelectEnclosedPoints()
    enclosedPts.SetInputData(vtkObj)
    enclosedPts.SetSurfaceData(surf3D)
    enclosedPts.SetTolerance(tol)
    # enclosedPts.SetCheckSurface(1)
    enclosedPts.Update()
    if RETURNTYPE.lower() == "polydata":
        vtkpts = vtk.vtkPoints()
        for i in range(vtkObj.GetNumberOfPoints()):
            if enclosedPts.IsInside(i):
                vtkpts.InsertNextPoint(vtkObj.GetPoint(i))
        # Create a new vtkPolyData to hold the inside points
        vtkpts_pd = vtk.vtkPolyData()
        vtkpts_pd.SetPoints(vtkpts)
        return vtkpts_pd
        # tt = filterThreshold(enclosedPts.GetOutput(), "SelectedPoints", 0.5, 2)
        # return polyDataFromVtkObj(tt)
    elif RETURNTYPE.lower() == "tf":
        selectedA = getArrayAsNumpy(enclosedPts.GetOutput(), "SelectedPoints")
        return selectedA > 0.5
    elif RETURNTYPE.lower() == "id":
        selectedA = getArrayAsNumpy(enclosedPts.GetOutput(), "SelectedPoints")
        tf = selectedA > 0.5
        return np.squeeze(np.argwhere(tf))
    return enclosedPts.GetOutput()

def filterGetArrayValuesWithinSurface(data, surf3D, arrayName):
    A = getArrayAsNumpy(data, arrayName=arrayName)
    ids2 = filterGetPointIDsInsideSurface(data, surf3D=surf3D)
    return A[ids2]










# ======================================================================================================================
#           VTK CONNECTED REGION FILTERS
# ======================================================================================================================
def __getConnectedRegionLargest_UnStruct(data: vtk.vtkDataObject) -> vtk.vtkPolyData:
    connectFilter = vtk.vtkConnectivityFilter()
    connectFilter.SetInputData(data)
    connectFilter.SetExtractionModeToLargestRegion()
    connectFilter.AddSpecifiedRegion(1)
    connectFilter.Update()
    return connectFilter.GetOutput()


def getConnectedRegionLargest(data: vtk.vtkDataObject) -> vtk.vtkPolyData:
    if not data.IsA('vtkPolyData'):
        return __getConnectedRegionLargest_UnStruct(data)
    connectFilter = vtk.vtkPolyDataConnectivityFilter()
    connectFilter.SetInputData(data)
    connectFilter.SetExtractionModeToLargestRegion()
    connectFilter.AddSpecifiedRegion(1)
    connectFilter.Update()
    return connectFilter.GetOutput()


def getConnectedRegionContaining(data: vtk.vtkDataObject, vtkId: int) -> vtk.vtkPolyData:
    connectFilter = vtk.vtkPolyDataConnectivityFilter()
    connectFilter.SetInputData(data)
    connectFilter.AddSeed(vtkId)
    connectFilter.Update()
    return connectFilter.GetOutput()


def getConnectedRegionClosestToX(data: vtk.vtkDataObject, X: np.ndarray) -> vtk.vtkPolyData:
    connectFilter = vtk.vtkPolyDataConnectivityFilter()
    connectFilter.SetInputData(data)
    connectFilter.SetExtractionModeToClosestPointRegion()
    connectFilter.SetClosestPoint(X[0], X[1], X[2])
    connectFilter.Update()
    return connectFilter.GetOutput()


def getConnectedRegionClosestToX_UnStruct(data: vtk.vtkDataObject, X: np.ndarray) -> vtk.vtkPolyData:
    connectFilter = vtk.vtkConnectivityFilter()
    connectFilter.SetInputData(data)
    connectFilter.SetExtractionModeToClosestPointRegion()
    connectFilter.SetClosestPoint(X[0], X[1], X[2])
    connectFilter.Update()
    return connectFilter.GetOutput()


def getConnectedRegionAll(data: vtk.vtkDataObject, minPts: Optional[int] = None) -> List[vtk.vtkPolyData]:
    connectFilter = vtk.vtkPolyDataConnectivityFilter()
    connectFilter.SetInputData(data)
    connectFilter.SetExtractionModeToSpecifiedRegions()
    connectFilter.InitializeSpecifiedRegionList()
    output, c1 = [], 0
    while True:
        connectFilter.AddSpecifiedRegion(c1)
        connectFilter.Update()
        thisRegion = vtk.vtkPolyData()
        thisRegion.DeepCopy(connectFilter.GetOutput())
        if thisRegion.GetNumberOfCells() <= 0:
            break
        output.append(thisRegion)
        connectFilter.DeleteSpecifiedRegion(c1)
        c1 += 1
    ##
    output = [cleanData(i, DO_POINT_MERGING=False) for i in output]
    if minPts is not None:
        output = [i for i in output if i.GetNumberOfPoints() >= minPts]
    outputS = sorted(output, key=lambda pp : pp.GetNumberOfPoints(), reverse=True)
    return outputS


def getConnectedRegionMinDistToX(data: vtk.vtkDataObject, X: np.ndarray, minNPts: int = 10) -> vtk.vtkPolyData:
    """
    Like closest to X - but min dist on pt by pt (rather than closest center point
    :param data:
    :param X:
    :param minNPts: default 10
    :return:
    """
    allRegions = getConnectedRegionAll(data, minNPts)
    ID = 0
    minDD = np.min(ftk.distPointPoints(X, getPtsAsNumpy(allRegions[0])))
    for k1 in range(1, len(allRegions)):
        dd = np.min(ftk.distPointPoints(X, getPtsAsNumpy(allRegions[k1])))
        if dd < minDD:
            minDD = dd
            ID = k1
    return allRegions[ID]




