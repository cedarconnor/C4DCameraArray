import c4d
from c4d import gui, plugins, bitmaps
from c4d.modules import takesystem
import math
import os
import json

# Plugin IDs - you should get official IDs from Plugin Cafe
PLUGIN_ID = 1054321

# Import resource symbols
exec(open(os.path.join(os.path.dirname(__file__), "res", "description", "camera_array_tool.h")).read())

class CameraArrayTool(plugins.ObjectData):
    """Advanced Camera Array Tool for Cinema 4D"""
    
    def __init__(self):
        self.created_cameras = []
        self.preview_objects = []
    
    def Init(self, node, isCloneInit=False):
        """Initialize the object with default values"""
        data = node.GetDataInstance()
        
        # Set default values
        data.SetLong(ARRAY_PATTERN, PATTERN_SPHERE)
        data.SetLong(CAMERA_COUNT, 12)
        data.SetReal(RADIUS, 200.0)
        data.SetReal(HEIGHT, 400.0)
        data.SetLong(GRID_SIZE_X, 3)
        data.SetLong(GRID_SIZE_Y, 3)
        data.SetLong(DIRECTION, DIR_INWARD)
        data.SetReal(FOCAL_LENGTH, 35.0)
        data.SetBool(SYNC_FOCAL_LENGTH, True)
        data.SetBool(CREATE_TAKES, True)
        data.SetBool(SHOW_PREVIEW, False)
        
        return True
    
    def Message(self, node, type, data):
        """Handle button messages"""
        if type == c4d.MSG_DESCRIPTION_COMMAND:
            id = data['id'][0].id
            
            if id == CREATE_ARRAY:
                self.create_camera_array(node)
            elif id == EXPORT_COLMAP:
                self.export_colmap(node)
            elif id == CLEAR_CAMERAS:
                self.clear_cameras(node)
            
            c4d.EventAdd()
            
        return True
    
    def GetDDescription(self, node, description, flags):
        """Dynamic description based on array pattern"""
        if not description.LoadDescription(node.GetType()):
            return False
            
        data = node.GetDataInstance()
        pattern = data.GetLong(ARRAY_PATTERN)
        
        # Hide/show parameters based on pattern
        desc = description.GetParameterI(RADIUS, None)
        if desc:
            desc[c4d.DESC_HIDE] = pattern == PATTERN_VERTICES
            
        desc = description.GetParameterI(HEIGHT, None)
        if desc:
            desc[c4d.DESC_HIDE] = pattern not in [PATTERN_CYLINDER]
            
        desc = description.GetParameterI(GRID_SIZE_X, None)
        if desc:
            desc[c4d.DESC_HIDE] = pattern != PATTERN_GRID
            
        desc = description.GetParameterI(GRID_SIZE_Y, None)
        if desc:
            desc[c4d.DESC_HIDE] = pattern != PATTERN_GRID
            
        desc = description.GetParameterI(CAMERA_COUNT, None)
        if desc:
            desc[c4d.DESC_HIDE] = pattern in [PATTERN_VERTICES, PATTERN_GRID]
        
        return True, flags | c4d.DESCFLAGS_DESC_LOADED
    
    def create_camera_array(self, node):
        """Create camera array based on current settings"""
        doc = node.GetDocument()
        if not doc:
            return
            
        data = node.GetDataInstance()
        pattern = data.GetLong(ARRAY_PATTERN)
        
        doc.StartUndo()
        
        # Clear existing cameras
        self.clear_cameras(node, add_undo=False)
        
        if pattern == PATTERN_VERTICES:
            cameras = self.create_vertex_cameras(node)
        elif pattern == PATTERN_SPHERE:
            cameras = self.create_sphere_cameras(node)
        elif pattern == PATTERN_CYLINDER:
            cameras = self.create_cylinder_cameras(node)
        elif pattern == PATTERN_GRID:
            cameras = self.create_grid_cameras(node)
        
        self.created_cameras = cameras
        
        # Apply focal length sync
        if data.GetBool(SYNC_FOCAL_LENGTH):
            self.sync_focal_length(cameras, data.GetReal(FOCAL_LENGTH))
        
        # Create takes if requested
        if data.GetBool(CREATE_TAKES):
            self.add_cameras_to_take_system(cameras)
        
        doc.EndUndo()
        c4d.EventAdd()
        
        gui.MessageDialog(f'Created {len(cameras)} cameras successfully!')
    
    def create_vertex_cameras(self, node):
        """Create cameras at polygon vertices"""
        doc = node.GetDocument()
        selected_obj = doc.GetActiveObject()
        
        if not selected_obj or selected_obj.GetType() != c4d.Opolygon:
            gui.MessageDialog('Please select a polygon object for vertex mode.')
            return []
        
        data = node.GetDataInstance()
        direction_type = data.GetLong(DIRECTION)
        target_obj = data.GetLink(TARGET_OBJECT)
        
        points = selected_obj.GetAllPoints()
        cameras = []
        
        for i, point in enumerate(points):
            cam = self.create_single_camera(f'VertexCam_{i+1}', point, direction_type, target_obj, selected_obj)
            if cam:
                cameras.append(cam)
                doc.InsertObject(cam, node)
                doc.AddUndo(c4d.UNDOTYPE_NEW, cam)
        
        return cameras
    
    def create_sphere_cameras(self, node):
        """Create cameras in spherical array"""
        doc = node.GetDocument()
        data = node.GetDataInstance()
        
        count = data.GetLong(CAMERA_COUNT)
        radius = data.GetReal(RADIUS)
        direction_type = data.GetLong(DIRECTION)
        target_obj = data.GetLink(TARGET_OBJECT)
        
        cameras = []
        
        # Golden spiral distribution for even spacing
        for i in range(count):
            # Golden angle in radians
            golden_angle = math.pi * (3.0 - math.sqrt(5.0))
            
            # y goes from 1 to -1
            y = 1 - (i / float(count - 1)) * 2
            
            # radius at y
            radius_at_y = math.sqrt(1 - y * y)
            
            # golden angle increment
            theta = golden_angle * i
            
            x = math.cos(theta) * radius_at_y
            z = math.sin(theta) * radius_at_y
            
            position = c4d.Vector(x * radius, y * radius, z * radius)
            
            cam = self.create_single_camera(f'SphereCam_{i+1}', position, direction_type, target_obj)
            if cam:
                cameras.append(cam)
                doc.InsertObject(cam, node)
                doc.AddUndo(c4d.UNDOTYPE_NEW, cam)
        
        return cameras
    
    def create_cylinder_cameras(self, node):
        """Create cameras in cylindrical array"""
        doc = node.GetDocument()
        data = node.GetDataInstance()
        
        count = data.GetLong(CAMERA_COUNT)
        radius = data.GetReal(RADIUS)
        height = data.GetReal(HEIGHT)
        direction_type = data.GetLong(DIRECTION)
        target_obj = data.GetLink(TARGET_OBJECT)
        
        cameras = []
        
        # Distribute cameras around cylinder
        for i in range(count):
            angle = (i / float(count)) * 2 * math.pi
            
            # Vary height for more interesting distribution
            y_offset = (i % 3 - 1) * height / 6  # Create 3 height levels
            
            x = math.cos(angle) * radius
            z = math.sin(angle) * radius
            y = y_offset
            
            position = c4d.Vector(x, y, z)
            
            cam = self.create_single_camera(f'CylinderCam_{i+1}', position, direction_type, target_obj)
            if cam:
                cameras.append(cam)
                doc.InsertObject(cam, node)
                doc.AddUndo(c4d.UNDOTYPE_NEW, cam)
        
        return cameras
    
    def create_grid_cameras(self, node):
        """Create cameras in grid array"""
        doc = node.GetDocument()
        data = node.GetDataInstance()
        
        size_x = data.GetLong(GRID_SIZE_X)
        size_y = data.GetLong(GRID_SIZE_Y)
        radius = data.GetReal(RADIUS)  # Use as spacing
        direction_type = data.GetLong(DIRECTION)
        target_obj = data.GetLink(TARGET_OBJECT)
        
        cameras = []
        
        # Create grid
        for x in range(size_x):
            for y in range(size_y):
                pos_x = (x - (size_x - 1) / 2.0) * radius
                pos_y = (y - (size_y - 1) / 2.0) * radius
                pos_z = radius  # Place grid in front
                
                position = c4d.Vector(pos_x, pos_y, pos_z)
                
                cam = self.create_single_camera(f'GridCam_{x}_{y}', position, direction_type, target_obj)
                if cam:
                    cameras.append(cam)
                    doc.InsertObject(cam, node)
                    doc.AddUndo(c4d.UNDOTYPE_NEW, cam)
        
        return cameras
    
    def create_single_camera(self, name, position, direction_type, target_obj=None, reference_obj=None):
        """Create a single camera with proper orientation"""
        cam = c4d.BaseObject(c4d.Ocamera)
        cam.SetName(name)
        cam.SetAbsPos(position)
        
        # Calculate direction based on type
        if direction_type == DIR_INWARD:
            if target_obj:
                target_pos = target_obj.GetAbsPos()
            else:
                target_pos = c4d.Vector(0, 0, 0)
            direction = (target_pos - position).GetNormalized()
        elif direction_type == DIR_OUTWARD:
            if target_obj:
                target_pos = target_obj.GetAbsPos()
            else:
                target_pos = c4d.Vector(0, 0, 0)
            direction = (position - target_pos).GetNormalized()
        elif direction_type == DIR_TANGENTIAL:
            # Tangential to sphere
            center = target_obj.GetAbsPos() if target_obj else c4d.Vector(0, 0, 0)
            to_center = (center - position).GetNormalized()
            up = c4d.Vector(0, 1, 0)
            direction = to_center.Cross(up).GetNormalized()
        else:  # DIR_CUSTOM
            direction = c4d.Vector(0, 0, -1)  # Default forward
        
        # Create orientation matrix
        self.orient_camera_to_direction(cam, direction)
        
        return cam
    
    def orient_camera_to_direction(self, camera, direction):
        """Orient camera to look in specified direction"""
        up_vector = c4d.Vector(0, 1, 0)
        right_vector = up_vector.Cross(direction).GetNormalized()
        
        # Handle case where direction is parallel to up
        if right_vector.GetLength() < 0.001:
            right_vector = c4d.Vector(1, 0, 0)
            up_vector = direction.Cross(right_vector).GetNormalized()
        else:
            up_vector = direction.Cross(right_vector).GetNormalized()
        
        position = camera.GetAbsPos()
        matrix = c4d.Matrix(position, right_vector, up_vector, direction)
        camera.SetMg(matrix)
    
    def sync_focal_length(self, cameras, focal_length):
        """Synchronize focal length across all cameras"""
        for cam in cameras:
            cam[c4d.CAMERAOBJECT_FOV] = math.radians(focal_length)
    
    def add_cameras_to_take_system(self, cameras):
        """Add cameras to take system"""
        if not cameras:
            return
            
        doc = cameras[0].GetDocument()
        take_data = doc.GetTakeData()
        
        if not take_data:
            gui.MessageDialog('No Take Data available in the document.')
            return
        
        main_take = take_data.GetMainTake()
        
        for camera in cameras:
            new_take = take_data.AddTake(camera.GetName(), main_take, None)
            new_take.SetCamera(take_data, camera)
    
    def clear_cameras(self, node, add_undo=True):
        """Clear all created cameras"""
        doc = node.GetDocument()
        if not doc:
            return
            
        if add_undo:
            doc.StartUndo()
        
        for cam in self.created_cameras:
            if cam.GetDocument():  # Check if still in document
                if add_undo:
                    doc.AddUndo(c4d.UNDOTYPE_DELETE, cam)
                cam.Remove()
        
        self.created_cameras = []
        
        if add_undo:
            doc.EndUndo()
    
    def export_colmap(self, node):
        """Export camera data in COLMAP format"""
        if not self.created_cameras:
            gui.MessageDialog('No cameras to export. Create an array first.')
            return
        
        # Get export path
        path = c4d.storage.SaveDialog(c4d.FILESELECTTYPE_ANYTHING, 
                                     "Export COLMAP Data", 
                                     c4d.FILESELECT_SAVE,
                                     "cameras.txt")
        
        if not path:
            return
        
        try:
            self.write_colmap_cameras(path)
            gui.MessageDialog(f'COLMAP data exported to {path}')
        except Exception as e:
            gui.MessageDialog(f'Export failed: {str(e)}')
    
    def write_colmap_cameras(self, filepath):
        """Write COLMAP cameras.txt file"""
        with open(filepath, 'w') as f:
            f.write("# Camera list with one line of data per camera:\n")
            f.write("# CAMERA_ID, MODEL, WIDTH, HEIGHT, PARAMS[]\n")
            
            for i, cam in enumerate(self.created_cameras):
                # Get render resolution from render settings
                doc = cam.GetDocument()
                rd = doc.GetActiveRenderData()
                width = rd[c4d.RDATA_XRES]
                height = rd[c4d.RDATA_YRES]
                
                # Get focal length
                fov = cam[c4d.CAMERAOBJECT_FOV]
                focal_length = width / (2.0 * math.tan(fov / 2.0))
                
                f.write(f"{i+1} PINHOLE {width} {height} {focal_length} {focal_length} {width/2} {height/2}\n")
        
        # Also write images.txt with camera poses
        images_path = filepath.replace('cameras.txt', 'images.txt')
        with open(images_path, 'w') as f:
            f.write("# Image list with two lines of data per image:\n")
            f.write("# IMAGE_ID, QW, QX, QY, QZ, TX, TY, TZ, CAMERA_ID, NAME\n")
            f.write("# POINTS2D[] as (X, Y, POINT3D_ID)\n")
            
            for i, cam in enumerate(self.created_cameras):
                # Get camera matrix
                mg = cam.GetMg()
                pos = mg.off
                
                # Convert rotation matrix to quaternion (simplified)
                # This is a basic conversion - for production use a proper library
                qw = math.sqrt(1.0 + mg.v1.x + mg.v2.y + mg.v3.z) / 2.0
                qx = (mg.v3.y - mg.v2.z) / (4.0 * qw)
                qy = (mg.v1.z - mg.v3.x) / (4.0 * qw)
                qz = (mg.v2.x - mg.v1.y) / (4.0 * qw)
                
                f.write(f"{i+1} {qw} {qx} {qy} {qz} {pos.x} {pos.y} {pos.z} {i+1} {cam.GetName()}.jpg\n")
                f.write("\n")  # Empty line for points2D

def main():
    """Register the plugin"""
    bmp = bitmaps.BaseBitmap()
    bmp.InitWith(os.path.join(os.path.dirname(__file__), "res", "icon.png"))
    
    plugins.RegisterObjectPlugin(
        id=PLUGIN_ID,
        str="Camera Array Tool",
        g=CameraArrayTool,
        description="camera_array_tool",
        icon=bmp,
        info=c4d.OBJECT_GENERATOR | c4d.OBJECT_INPUT
    )

if __name__ == '__main__':
    main()
