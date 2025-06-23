Welcome to Ngawari's documentation!
====================================

.. image:: https://img.shields.io/pypi/v/ngawari.svg
   :target: https://pypi.org/project/ngawari/
   :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/ngawari.svg
   :target: https://pypi.org/project/ngawari/
   :alt: Python versions

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
   :target: https://github.com/fraser29/ngawari/blob/main/LICENSE
   :alt: License

**Ngawari** is a simple and functional toolkit for working with data in VTK (Visualization Toolkit). 
It provides a comprehensive set of utilities for VTK data manipulation, filtering, and processing.

Key Features
------------

* **VTK Data Utilities**: Functions for working with VTK data objects (vtkImageData, vtkPolyData, vtkStructuredGrid)
* **Array Management**: Easy conversion between VTK arrays and NumPy arrays
* **Filtering Operations**: Comprehensive set of VTK filters and operations
* **Geometry Tools**: Utilities for building and manipulating geometric objects
* **File I/O**: Simplified reading and writing of VTK file formats
* **Mathematical Operations**: Vector and matrix operations optimized for VTK data

Quick Start
-----------

.. code-block:: python

   import ngawari as ng
   import vtk
   
   # Create a simple sphere
   sphere = ng.buildSphereSource([0, 0, 0], radius=1.0)
   
   # Get points as numpy array
   points = ng.getPtsAsNumpy(sphere)
   
   # Add a scalar array
   ng.setArrayFromNumpy(sphere, points[:, 0], "x_coords", SET_SCALAR=True)
   
   # Apply a filter
   smoothed = ng.smoothTris(sphere, iterations=10)

Installation
------------

.. code-block:: bash

   pip install ngawari

For development installation with documentation dependencies:

.. code-block:: bash

   pip install ngawari[docs]

Documentation Structure
----------------------

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   quickstart
   api/index
   examples/index
   contributing

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search` 