import c4d
from c4d import gui
from c4d.modules import takesystem
import math

def create_cameras_from_vertices():
    # Get the active document
    doc = c4d.documents.GetActiveDocument()
    obj = doc.GetActiveObject()

    if not obj or obj.GetType() != c4d.Opolygon:
        gui.MessageDialog('Please select a polygon object.')
        return

    doc.StartUndo()  # Start recording undo actions

    # Get the points (vertices) of the object
    points = obj.GetAllPoints()

    created_cameras = []

    for i, point in enumerate(points):
        # Create a new camera
        cam = c4d.BaseObject(c4d.Ocamera)
        cam.SetName(f'Camera_{i+1}')

        # Set the camera's position to the vertex position
        cam.SetAbsPos(point)

        # Calculate the direction from the camera to the world origin
        direction = c4d.Vector(0, 0, 0) - point
        direction.Normalize()

        # Create a matrix to orient the camera towards the origin
        up_vector = c4d.Vector(0, 1, 0)  # World up direction
        right_vector = up_vector.Cross(direction).GetNormalized()
        up_vector = direction.Cross(right_vector).GetNormalized()

        matrix = c4d.Matrix(point, right_vector, up_vector, direction)
        cam.SetMg(matrix)

        # Insert the camera into the document
        doc.InsertObject(cam)
        doc.AddUndo(c4d.UNDOTYPE_NEW, cam)

        created_cameras.append(cam)

    doc.EndUndo()  # Stop recording undo actions
    c4d.EventAdd()

    return created_cameras

def add_cameras_to_take_system(cameras):
    # Get the active document
    doc = c4d.documents.GetActiveDocument()

    # Get the take data for the current document
    take_data = doc.GetTakeData()
    if not take_data:
        gui.MessageDialog('No Take Data available in the document.')
        return

    # Get the main take (the root take)
    main_take = take_data.GetMainTake()

    if not cameras:
        gui.MessageDialog('No cameras created.')
        return

    # Iterate through each created camera and create a new take for it
    for camera in cameras:
        # Create a new take for each camera
        new_take = take_data.AddTake(camera.GetName(), main_take, None)

        # Set the camera for the take
        new_take.SetCamera(take_data, camera)

        # Optionally, print out some info for debugging
        print(f"Created take for camera: {camera.GetName()}")

    # Tell Cinema 4D to update the scene
    c4d.EventAdd()

def main():
    # Step 1: Create cameras at each vertex
    cameras = create_cameras_from_vertices()

    # Step 2: Add the created cameras to the take system
    if cameras:
        add_cameras_to_take_system(cameras)

if __name__ == '__main__':
    main()
