
import vtk
from vtk.util import numpy_support # type: ignore
import numpy as np
from typing import List, Dict, Optional

# ======================================================================================================================
#           VTK NUMPY SUPPORT HELPERS
# ======================================================================================================================
def getArrayNames(data: vtk.vtkDataObject, pointData: bool = True) -> List[str]:
    """
    Get the list of array names from a VTK data object.

    Args:
        data (vtk.vtkDataObject): The VTK data object.
        pointData (bool): Whether to get point data arrays.

    Returns:
        List[str]: The list of array names.
    """
    if pointData:
        return [data.GetPointData().GetArrayName(i) for i in range(data.GetPointData().GetNumberOfArrays())]
    else:
        return [data.GetCellData().GetArrayName(i) for i in range(data.GetCellData().GetNumberOfArrays())]


def getArray(data: vtk.vtkDataObject, arrayName: str, pointData: bool = True) -> vtk.vtkAbstractArray:
    """
    Get an array from a VTK data object.

    Args:
        data (vtk.vtkDataObject): The VTK data object.
        arrayName (str): The name of the array to get.
        pointData (bool): Whether to get point data arrays.

    Returns:
        vtk.vtkAbstractArray: The array.
    """
    if pointData:
        return data.GetPointData().GetAbstractArray(arrayName)
    else:
        return data.GetCellData().GetAbstractArray(arrayName)


def getArrayAsNumpy(data: vtk.vtkDataObject, arrayName: str, pointData: bool = True) -> np.ndarray:
    """
    Get an array from a VTK data object as a numpy array.

    Args:
        data (vtk.vtkDataObject): The VTK data object.
        arrayName (str): The name of the array to get.
        pointData (bool): Whether to get point data arrays.

    Returns:
        np.ndarray: The array.
    """
    array = getArray(data, arrayName, pointData)
    return numpy_support.vtk_to_numpy(array)    


def getScalarsArrayName(data: vtk.vtkDataObject, pointData: bool = True) -> Optional[str]:
    """
    Get the name of the scalars array from a VTK data object.

    Args:
        data (vtk.vtkDataObject): The VTK data object.
        pointData (bool): Whether to get point data arrays [default: True].
    Returns:
        str: The name of the scalars array (None if none found)
    """
    aS = data.GetPointData().GetScalars() if pointData else data.GetCellData().GetScalars()
    try:
        return aS.GetName()
    except AttributeError: # in case no scalars set
        return None


def getVectorsArrayName(data: vtk.vtkDataObject, pointData: bool = True) -> Optional[str]:
    aS = data.GetPointData().GetVectors() if pointData else data.GetCellData().GetVectors()
    try:
        return aS.GetName()
    except AttributeError: # in case no scalars set
        return None


def getArrayId(data: vtk.vtkDataObject, arrayName: str, pointData: bool = True) -> Optional[int]:
    """
    Get the index of an array in a VTK data object.

    Args:
        data (vtk.vtkDataObject): The VTK data object.
        arrayName (str): The name of the array to get.
        pointData (bool): Whether to get point data arrays.

    Returns:
        Optional[int]: The index of the array.
    """
    if pointData:
        for i in range(data.GetPointData().GetNumberOfArrays()):
            if arrayName == data.GetPointData().GetArrayName(i):
                return i
    else:
        for i in range(data.GetCellData().GetNumberOfArrays()):
            if arrayName == data.GetCellData().GetArrayName(i):
                return i
    return None


def renameArray(data: vtk.vtkDataObject, arrayNameOld: str, arrayNameNew: str, pointData: bool = True) -> None:
    if pointData:
        data.GetPointData().GetArray(arrayNameOld).SetName(arrayNameNew)
    else:
        data.GetCellData().GetArray(arrayNameOld).SetName(arrayNameNew)


def getArrayAsNumpy(data: vtk.vtkDataObject, arrayName: str, RETURN_3D: bool = False, pointData: bool = True) -> np.ndarray:
    """
    Get an array from a VTK data object as a numpy array.

    Args:
        data (vtk.vtkDataObject): The VTK data object.
        arrayName (str): The name of the array.
        RETURN_3D (bool): Whether to return a 3D array [default: False].
        pointData (bool): Whether to get point data arrays [default: True].
    Returns:
        np.ndarray: The array.
    """
    A = numpy_support.vtk_to_numpy(getArray(data, arrayName, pointData)).copy()
    if RETURN_3D:
        if np.ndim(A) == 2:
            return np.reshape(A, list(data.GetDimensions())+[A.shape[1]], 'F')
        else:
            return np.reshape(A, data.GetDimensions(), 'F')
    else:
        return A


def getScalarsAsNumpy(data: vtk.vtkDataObject, pointData: bool = True) -> np.ndarray:
    if pointData:   
        return numpy_support.vtk_to_numpy(data.GetPointData().GetScalars()).copy()
    else:
        return numpy_support.vtk_to_numpy(data.GetCellData().GetScalars()).copy()


# ======================================================================================================================
#           SET ARRAYS
# ======================================================================================================================
def addNpArray(data: vtk.vtkDataObject, npArray: np.ndarray, arrayName: str, SET_SCALAR: bool = False, SET_VECTOR: bool = False, IS_3D: bool = False, pointData: bool = True) -> None:
    """
    Add a numpy array to a VTK data object.

    Args:
        data (vtk.vtkDataObject): The VTK data object.
        npArray (np.ndarray): The numpy array.
        arrayName (str): The name of the array.
        SET_SCALAR (bool): Whether to set the array as scalars.
        SET_VECTOR (bool): Whether to set the array as vectors.
        IS_3D (bool): Whether the array is 3D.
        pointData (bool): Whether to add point data arrays [default: True].
    """
    if getArrayId(data, arrayName, pointData) is not None:
        if pointData:
            data.GetPointData().RemoveArray(arrayName)
        else:
            data.GetCellData().RemoveArray(arrayName)
    if IS_3D:
        if np.ndim(npArray) == 4:
            npArray = np.reshape(npArray, (np.prod(npArray.shape[:3]), 3), 'F')
        else:
            npArray = np.reshape(npArray, np.prod(data.GetDimensions()), 'F')
    aArray = numpy_support.numpy_to_vtk(npArray, deep=1)
    aArray.SetName(arrayName)
    if SET_SCALAR:
        if pointData:
            data.GetPointData().SetScalars(aArray)
        else:
            data.GetCellData().SetScalars(aArray)
    elif SET_VECTOR:
        if pointData:
            data.GetPointData().SetVectors(aArray)
        else:
            data.GetCellData().SetVectors(aArray)
    else:
        if pointData:
            data.GetPointData().AddArray(aArray)
        else:
            data.GetCellData().AddArray(aArray)


def setArrayDtype(data: vtk.vtkDataObject, arrayName: str, dtype: np.dtype, SET_SCALAR: bool = False, pointData: bool = True) -> None:
    A = getArrayAsNumpy(data, arrayName, pointData)
    addNpArray(data, A.astype(dtype), arrayName, SET_SCALAR=SET_SCALAR, pointData=pointData)


def setArrayAsScalars(data: vtk.vtkDataObject, arrayName: str, pointData: bool = True) -> None:
    if pointData:
        data.GetPointData().SetScalars(getArray(data, arrayName, pointData))
    else:
        data.GetCellData().SetScalars(getArray(data, arrayName, pointData))


def ensureScalarsSet(data: vtk.vtkDataObject, possibleName: Optional[str] = None, pointData: bool = True) -> str:
    aS = data.GetPointData().GetScalars() if pointData else data.GetCellData().GetScalars()
    try:
        return aS.GetName()
    except AttributeError: # in case no scalars set
        names = getArrayNames(data, pointData)
        if possibleName is not None:
            if possibleName in names:
                setArrayAsScalars(data, possibleName, pointData)
                return possibleName
        setArrayAsScalars(data, names[0], pointData)
        return names[0]


# ======================================================================================================================
#           DELETE ARRAYS
# ======================================================================================================================
def delArray(data: vtk.vtkDataObject, arrayName: str, pointData: bool = True) -> None:
    """
    Delete an array from a VTK data object.

    Args:
        data (vtk.vtkDataObject): The VTK data object.
        arrayName (str): The name of the array to delete.
        pointData (bool): Whether to delete point data arrays [default: True].
    """
    if pointData:
        data.GetPointData().RemoveArray(arrayName)
    else:
        data.GetCellData().RemoveArray(arrayName)


def delArraysExcept(data: vtk.vtkDataObject, arrayNamesToKeep_list: List[str], pointData: bool = True) -> vtk.vtkDataObject:
    """
    Delete all arrays except the specified ones.

    Args:
        data (vtk.vtkDataObject): The VTK data object.
        arrayNamesToKeep_list (List[str]): The list of array names to keep.
        pointData (bool): Whether to delete point data arrays [default: True].
    Returns:
        vtk.vtkDataObject: The data object with the specified arrays kept.
    """
    for ia in getArrayNames(data, pointData):
        if ia not in arrayNamesToKeep_list:
            delArray(data, ia, pointData)
    return data


# ======================================================================================================================
#           VTK FIELD DATA
# ======================================================================================================================
def addFieldData(data: vtk.vtkDataObject, fieldVal: float, fieldName: str) -> None:
    tagArray = numpy_support.numpy_to_vtk(np.array([float(fieldVal)]))
    tagArray.SetName(fieldName)
    data.GetFieldData().AddArray(tagArray)


def getFieldData(data: vtk.vtkDataObject, fieldName: str) -> np.ndarray:
    return numpy_support.vtk_to_numpy(data.GetFieldData().GetArray(fieldName)).copy()


def getFieldDataDict(data: vtk.vtkDataObject) -> Dict[str, np.ndarray]:
    """
    Get the field data as a dictionary. Note: will skip strings.

    Args:
        data (vtk.vtkDataObject): The VTK data object.

    Returns:
        Dict[str, np.ndarray]: The field data.
    """
    dictOut = {}
    for fieldName in getFieldDataNames(data):
        try:
            dictOut[fieldName] = numpy_support.vtk_to_numpy(data.GetFieldData().GetArray(fieldName)).copy()
        except AttributeError: # str
            pass
    return dictOut


def getFieldDataNames(data: vtk.vtkDataObject) -> List[str]:
    """
    Get the field data names from a VTK data object.

    Args:
        data (vtk.vtkDataObject): The VTK data object.

    Returns:
        List[str]: The field data names.
    """
    names = [data.GetFieldData().GetArrayName(i) for i in range(data.GetFieldData().GetNumberOfArrays())]
    return names


def dublicateFieldData(srcData: vtk.vtkDataObject, destData: vtk.vtkDataObject) -> None:
    """
    Duplicate the field data from one VTK data object to another.

    Args:
        srcData (vtk.vtkDataObject): The source VTK data object.
        destData (vtk.vtkDataObject): The destination VTK data object.
    """
    for i in range(srcData.GetFieldData().GetNumberOfArrays()):
        fName = srcData.GetFieldData().GetArrayName(i)
        try:
            val = numpy_support.vtk_to_numpy(srcData.GetFieldData().GetArray(fName))
            tagArray = numpy_support.numpy_to_vtk(val)
            tagArray.SetName(fName)
            destData.GetFieldData().AddArray(tagArray)
        except AttributeError:
            pass


def deleteFieldData(data: vtk.vtkDataObject) -> vtk.vtkDataObject:
    """
    Remove the field data from a VTK data object.

    Args:
        data (vtk.vtkDataObject): The VTK data object.

    Returns:
        vtk.vtkDataObject: The data object with the field data removed.
    """
    aNames = [data.GetFieldData().GetArrayName(i) for i in range(data.GetFieldData().GetNumberOfArrays())]
    for fName in aNames:
        print(f" rm {fName}")
        data.GetFieldData().RemoveArray(fName)
    return data


# ======================================================================================================================
#           VTK POINTS
# ======================================================================================================================
def getVtkPointsAsNumpy(data):
    return numpy_support.vtk_to_numpy(data.GetPoints().GetData())

def getPtsAsNumpy(data):
    if isVTI(data):
        return np.array([data.GetPoint(pointID) for pointID in range(data.GetNumberOfPoints())])
    return getVtkPointsAsNumpy(data)

