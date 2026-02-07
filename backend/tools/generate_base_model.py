import os

import numpy as np
from stl import mesh


def createBaseCylinder(filename="base_socket.stl", radius=50, height=200):
    """
    Creates a simple cylinder mesh to serve as a base prosthetic socket model.
    Saved to backend/assets/base_models/
    """
    # Create 8 vertices for a simplified rectangular prism (approximating a cylinder for MVP)
    # A real cylinder would use more vertices, but this is enough to prove numpy-stl works.
    # Actually, let's just make a cube for simplicity of generation,
    # or use numpy-stl's functionality if available,
    # but manually defining vertices is safer without external deps for generation logic.

    # Let's make a simple box for the "socket"
    # width = 2*radius, depth = 2*radius

    w = radius
    h = height

    # Define the 8 vertices of a cube centered at 0,0,0 for X-Y
    vertices = np.array([
        [-w, -w, 0],
        [+w, -w, 0],
        [+w, +w, 0],
        [-w, +w, 0],
        [-w, -w, h],
        [+w, -w, h],
        [+w, +w, h],
        [-w, +w, h],
    ])

    # Define the 12 triangles composing the cube
    faces = np.array([
        [0, 3, 1], [1, 3, 2],  # Bottom
        [0, 4, 7], [0, 7, 3],  # Left
        [4, 5, 6], [4, 6, 7],  # Top
        [5, 1, 2], [5, 2, 6],  # Right
        [2, 3, 6], [3, 7, 6],  # Back
        [0, 1, 5], [0, 5, 4]  # Front
    ])

    # Create the mesh
    socketMesh = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    for i, f in enumerate(faces):
        for j in range(3):
            socketMesh.vectors[i][j] = vertices[f[j], :]

    # Ensure directory exists
    # Go up one level from 'tools' to 'backend', then into 'assets/base_models'
    saveDir = os.path.join(os.path.dirname(__file__), "..", "assets", "base_models")
    os.makedirs(saveDir, exist_ok=True)

    savePath = os.path.join(saveDir, filename)
    socketMesh.save(savePath)
    print(f"Base model created at: {savePath}")


if __name__ == "__main__":
    createBaseCylinder()
