import json
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np

# Load your JSON data
with open("meshes.json", "r") as file:
    data = json.load(file)

current_index = 0  # Initialize current index


def plot_item(index):
    # Ensure the index is within bounds
    index = index % len(data)
    item = data[index]

    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")

    vertices = item["vertices"]
    polygons = item["polygons"]

    verts = [
        [
            (vertices[vi]["x"], vertices[vi]["y"], vertices[vi]["z"])
            for vi in poly["vertex_indices"]
        ]
        for poly in polygons
    ]

    poly3d = Poly3DCollection(verts, alpha=0.5)
    ax.add_collection3d(poly3d)

    scale = np.concatenate([np.array(v).flatten() for v in verts]).flatten()
    ax.auto_scale_xyz(scale, scale, scale)

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")

    # Setting up the key press event handler
    def on_key(event):
        nonlocal index  # Use nonlocal keyword to modify the outer variable
        if event.key == "right":
            index += 1
        elif event.key == "left":
            index -= 1
        plt.close(fig)  # Close the current figure to trigger a new plot
        plot_item(index)  # Recursively call plot_item with the new index

    fig.canvas.mpl_connect("key_press_event", on_key)
    plt.show()


# Initial call to plot the first item
plot_item(current_index)
