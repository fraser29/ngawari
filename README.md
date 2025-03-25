# Ngawari

Ngawari is a Python-based toolkit for simplifying operations in data analysis and processing, particularly focused on medical imaging and computational geometry. It is built heavily on top of the [VTK library](https://vtk.org/).

## Features

- Advanced geometric calculations and transformations
- Medical imaging data processing
- Statistical analysis tools
- 3D visualization capabilities

## Installation

To install Ngawari, run the following command:

```bash
pip install ngawari
```

## Usage

Here's a quick example of how to use Ngawari:

```python
from ngawari import ftk

# Calculate Body Surface Area
height_cm = 170
weight_kg = 70
bsa = ftk.calculateBSA(height_cm, weight_kg)
print(f"Body Surface Area: {bsa:.2f} m²")

# Fit a plane to 3D points
points = [[0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0]]
plane = ftk.fitPlaneToPoints(points)
print(f"Fitted plane coefficients: {plane}")
```

For more detailed usage instructions, please refer to the documentation.

## Documentation #TODO

Full documentation is available at [https://ngawari.readthedocs.io](https://ngawari.readthedocs.io)

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for more details.

## License

Ngawari is released under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Contact

For any questions or support, please open an issue on our [GitHub repository](https://github.com/fraser29/ngawari) or contact us at support@ngawari.com.

## Dependencies

This project uses the following major dependencies:
- VTK (BSD 3-Clause License) - https://vtk.org/ 