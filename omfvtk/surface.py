"""Methods to convert surface objects to VTK data objects"""


__all__ = [
    'surface_geom_to_vtk',
    'surface_grid_geom_to_vtk',
    'surface_to_vtk',
]

__displayname__ = 'Surface'

import vtk
from vtk.util import numpy_support as nps
import vtki
import omf

from PIL import Image
import numpy as np

def surface_geom_to_vtk(surfgeom):
    """Convert the triangulated surface to a :class:`vtki.UnstructuredGrid`
    object

    Args:
        surfgeom (:class:`omf.surface.SurfaceGeometry`): the surface geomotry to
            convert
    """

    output = vtk.vtkUnstructuredGrid()
    pts = vtk.vtkPoints()
    cells = vtk.vtkCellArray()

    # Generate the points
    pts.SetNumberOfPoints(surfgeom.num_nodes)
    pts.SetData(nps.numpy_to_vtk(surfgeom.vertices))

    # Generate the triangle cells
    cellConn = surfgeom.triangles.array
    cellsMat = np.concatenate(
        (np.ones((cellConn.shape[0], 1), dtype=np.int64)*cellConn.shape[1], cellConn),
        axis=1).ravel()
    cells = vtk.vtkCellArray()
    cells.SetNumberOfCells(cellConn.shape[0])
    cells.SetCells(cellConn.shape[0],
            nps.numpy_to_vtk(cellsMat, deep=True, array_type=vtk.VTK_ID_TYPE))

    # Add to output
    output.SetPoints(pts)
    output.SetCells(vtk.VTK_TRIANGLE, cells)
    return vtki.wrap(output)


def surface_grid_geom_to_vtk(surfgridgeom):
    """Convert the 2D grid to a :class:`vtki.StructuredGrid` object.

    Args:
        surfgridgeom (:class:`omf.surface.SurfaceGridGeometry`): the surface
            grid geometry to convert

    """

    output = vtk.vtkStructuredGrid()

    # TODO: calcualte the w vector that is perpendicular to U and V
    axis_w = [0, 0, 1]
    rotation_mtx = np.array([surfgridgeom.axis_u, surfgridgeom.axis_v, axis_w])
    ox, oy, oz = surfgridgeom.origin

    # Make coordinates along each axis
    x = ox + np.cumsum(surfgridgeom.tensor_u)
    x = np.insert(x, 0, ox)
    y = oy + np.cumsum(surfgridgeom.tensor_v)
    y = np.insert(y, 0, oy)

    z = np.array([oz])

    output.SetDimensions(len(x), len(y), len(z))

    # Build out all nodes in the mesh
    xx, yy, zz = np.meshgrid(x, y, z)
    points = np.c_[xx.flatten(), yy.flatten(), zz.flatten()]

    # Rotate the points based on the axis orientations
    points = points.dot(rotation_mtx)

    # Convert points to vtk object
    pts = vtk.vtkPoints()
    pts.SetNumberOfPoints(len(points))
    pts.SetData(nps.numpy_to_vtk(points))
    # Now build the output
    output.SetPoints(pts)

    return vtki.wrap(output)

def surface_to_vtk(surfel):
    """Convert the surface to a its appropriate VTK data object type.

    Args:
        surfel (:class:`omf.surface.SurfaceElement`): the surface element to
            convert
    """

    geom = surfel.geometry

    if isinstance(geom, omf.surface.SurfaceGeometry):
        builder = surface_geom_to_vtk
    elif isinstance(geom, omf.surface.SurfaceGridGeometry):
        builder = surface_grid_geom_to_vtk

    output = builder(geom)

    # Now add point data:
    for data in surfel.data:
        arr = data.array.array
        c = nps.numpy_to_vtk(num_array=arr)
        c.SetName(data.name)
        loc = data.location
        if loc == 'vertices':
            output.GetPointData().AddArray(c)
        else:
            output.GetCellData().AddArray(c)

    output = vtki.wrap(output)
    for i, tex in enumerate(surfel.textures):
        # Now map the coordinates for the texture
        m = vtk.vtkTextureMapToPlane()
        m.SetInputDataObject(output)
        m.SetOrigin(tex.origin)
        m.SetPoint1(tex.origin + tex.axis_u)
        m.SetPoint2(tex.origin + tex.axis_v)
        m.Update()
        # Grab the texture coordinates
        tmp = m.GetOutputDataObject(0)
        tcoord = tmp.GetPointData().GetTCoords()
        name = tex.name
        if name is None or name == '':
            name = '{}-texture-{}'.format(surfel.name, i)
        tcoord.SetName(name)
        # Add these coordinates to the PointData of the output
        # NOTE: Let vtki handle setting the TCoords because of how VTK cleans
        #       up old TCoords
        output.GetPointData().AddArray(tcoord)
        # Add the vtkTexture to the output
        img = np.array(Image.open(tex.image))
        tex.image.seek(0) # Reset the image bytes in case it is accessed again
        if img.shape[2] > 3:
            img = img[:, :, 0:3]
        vtexture = vtki.numpy_to_texture(img)
        output.textures[name] = vtexture

    return output


surface_to_vtk.__displayname__ = 'Surface to VTK'
surface_grid_geom_to_vtk.__displayname__ = 'Surface Grid Geometry to VTK'
surface_geom_to_vtk.__displayname__ = 'Surface Geometry to VTK'
