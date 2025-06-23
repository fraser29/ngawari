Quick Start Guide
=================

This guide will help you get started with Ngawari quickly. We'll cover the basic concepts and show you how to perform common tasks.

Basic Concepts
--------------

Ngawari provides utilities for working with VTK data objects. Three primary modules are provided:

* **ftk**: Mathematical and utility functions
* **fIO**: File input/output operations
* **vtkfilters**: VTK filtering and processing functions

Getting Started
--------------

First, import Ngawari:

.. code-block:: python

   from ngawari import ftk, fIO, vtkfilters

Creating Basic Geometry
----------------------

Create a sphere:

.. code-block:: python

   # Create a sphere at origin with radius 1.0
   sphere = vtkfilters.buildSphereSource([0, 0, 0], radius=1.0)
   print(f"Sphere has {sphere.GetNumberOfPoints()} points")

Create a cylinder:

.. code-block:: python

   # Create a cylinder
   cylinder = vtkfilters.buildCylinderSource([0, 0, 0], radius=0.5, height=2.0)
   print(f"Cylinder has {cylinder.GetNumberOfPoints()} points")

Working with Arrays
------------------

Get points as a NumPy array:

.. code-block:: python

   # Get all points from the sphere
   points = vtkfilters.getPtsAsNumpy(sphere)
   print(f"Points shape: {points.shape}")  # (n_points, 3)

Add a scalar array:

.. code-block:: python

   # Create a scalar array based on x-coordinates
   x_coords = points[:, 0]
   vtkfilters.setArrayFromNumpy(sphere, x_coords, "x_coordinates", SET_SCALAR=True)

Add a vector array:

.. code-block:: python

   # Create a vector array (example: normalized position vectors)
   import numpy as np
   vectors = points / np.linalg.norm(points, axis=1, keepdims=True)
   vtkfilters.setArrayFromNumpy(sphere, vectors, "normals", SET_VECTOR=True)

Filtering Operations
-------------------

Apply smoothing:

.. code-block:: python

   # Smooth the sphere
   smoothed = vtkfilters.smoothTris(sphere, iterations=10)

Extract surface from volume data:

.. code-block:: python

   # If you have volume data, extract the surface
   surface = vtkfilters.filterExtractSurface(volume_data)

Clipping and Cutting
-------------------

Clip by plane:

.. code-block:: python

   # Clip the sphere with a plane
   plane_point = [0, 0, 0]
   plane_normal = [1, 0, 0]  # x-direction
   clipped = vtkfilters.clipDataByPlane(sphere, plane_point, plane_normal)

Clip by sphere:

.. code-block:: python

   # Clip with a sphere
   clip_center = [0.5, 0, 0]
   clip_radius = 0.3
   clipped = vtkfilters.getPolyDataClippedBySphere(sphere, clip_center, clip_radius)

File I/O
--------

Save data to VTK format - file extension is used for format:

.. code-block:: python

   # Save polydata
   fIO.writeVTKFile(sphere, "sphere.vtp")
   
   # Save image data
   fIO.writeVTKFile(image_data, "image.vti")

Load data from VTK format:

.. code-block:: python

   # Load polydata
   loaded_sphere = fIO.readVTKFile("sphere.vtp")
   
   # Load image data
   loaded_image = fIO.readVTKFile("image.vti")

Mathematical Operations
----------------------

Calculate distances:

.. code-block:: python

   # Distance between two points
   point1 = [0, 0, 0]
   point2 = [1, 1, 1]
   distance = ftk.distTwoPoints(point1, point2)

Vector operations:

.. code-block:: python

   # Normalize a vector
   vector = [1, 2, 3]
   normalized = ftk.normaliseArray(vector)
   
   # Dot product
   vec1 = [1, 0, 0]
   vec2 = [0, 1, 0]
   dot_product = ftk.fcdot(vec1, vec2)

Complete Example
---------------

Here's a complete example that demonstrates several features:

.. code-block:: python

   from ngawari import ftk, fIO, vtkfilters
   import numpy as np
   
   # Create a sphere
   sphere = vtkfilters.buildSphereSource([0, 0, 0], radius=1.0)
   
   # Get points and add scalar data
   points = vtkfilters.getPtsAsNumpy(sphere)
   distances = np.linalg.norm(points, axis=1)
   vtkfilters.setArrayFromNumpy(sphere, distances, "distance_from_origin", SET_SCALAR=True)
   
   # Apply smoothing
   smoothed = vtkfilters.smoothTris(sphere, iterations=5)
   
   # Clip with a plane
   clipped = vtkfilters.clipDataByPlane(smoothed, [0, 0, 0], [1, 0, 0])
   
   # Save the result
   fIO.writeVTKFile(clipped, "clipped_sphere.vtp")
   
   print(f"Final result has {clipped.GetNumberOfPoints()} points")

Next Steps
----------

Now that you have the basics, you can explore:

* :doc:`api/index` - Complete API reference
* :doc:`examples/index` - More detailed examples
* :doc:`contributing` - How to contribute to the project

For more advanced usage, check out the individual module documentation:

* :doc:`api/ftk` - Mathematical and utility functions
* :doc:`api/fIO` - File input/output operations
* :doc:`api/vtkfilters` - VTK filtering and processing functions 