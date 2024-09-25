
# =========================================================================
def nxToVtk(G: nx.Graph, nodeLocationDict: Dict[int, List[float]]) -> vtk.vtkPolyData:
    """
    Convert a NetworkX graph to a VTK polydata.

    Args:
        G (nx.Graph): The NetworkX graph to convert.
        nodeLocationDict (Dict[int, List[float]]): A dictionary mapping node IDs to their coordinates.

    Returns:
        vtk.vtkPolyData: The VTK polydata object.
    """
    for n in G.nodes():
        try:
            nodeLocationDict[n]
        except KeyError:
            raise KeyError("node %s doesn't have position" % n)
    points = vtk.vtkPoints()
    vtkGraphPolyData = vtk.vtkPolyData()

    # Edges ## TODO - currently skipping unconnected nodes
    lines = vtk.vtkCellArray()
    i = 0
    IS_WEIGHTED = False
    for e in G.edges():
        IS_WEIGHTED = "weight" in G.get_edge_data(e[0],e[1])
        break
    if IS_WEIGHTED:
        weightA = np.zeros(len(G.edges()))
    for c1, e in enumerate(G.edges()):
        # The edge e can be a 2-tuple (Graph) or a 3-tuple (Xgraph)
        u = e[0]
        v = e[1]
        if v in nodeLocationDict and u in nodeLocationDict:
            lines.InsertNextCell(2)
            if IS_WEIGHTED:
                weightA[c1] = G.get_edge_data(u,v)["weight"]
            for n in (u, v):
                (x, y, z) = nodeLocationDict[n]
                points.InsertPoint(i, x, y, z)
                lines.InsertCellPoint(i)
                i = i + 1
    vtkGraphPolyData.SetPoints(points)
    vtkGraphPolyData.SetLines(lines)
    if IS_WEIGHTED:
        aArray = numpy_support.numpy_to_vtk(weightA, deep=1)
        aArray.SetName("weights")
        vtkGraphPolyData.GetCellData().AddArray(aArray)
    return vtkGraphPolyData