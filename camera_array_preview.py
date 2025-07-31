import c4d
import math

class CameraArrayPreview:
    """Preview system for camera array placement"""
    
    def __init__(self, parent_tool):
        self.parent_tool = parent_tool
        self.preview_objects = []
        self.preview_enabled = False
    
    def toggle_preview(self, node, enabled):
        """Toggle preview visualization"""
        self.preview_enabled = enabled
        
        if enabled:
            self.create_preview(node)
        else:
            self.clear_preview()
    
    def create_preview(self, node):
        """Create preview visualization of camera positions"""
        self.clear_preview()
        
        doc = node.GetDocument()
        if not doc:
            return
        
        data = node.GetDataInstance()
        pattern = data.GetLong(self.parent_tool.ARRAY_PATTERN)
        
        positions = self.get_camera_positions(node)
        
        # Create small cubes at camera positions
        for i, pos in enumerate(positions):
            cube = c4d.BaseObject(c4d.Ocube)
            cube.SetName(f'Preview_Cam_{i+1}')
            cube.SetAbsPos(pos)
            cube[c4d.PRIM_CUBE_LEN] = c4d.Vector(10, 10, 10)  # Small size
            
            # Set preview material (wireframe)
            mat = c4d.BaseMaterial(c4d.Mmaterial)
            mat.SetName('Preview_Material')
            mat[c4d.MATERIAL_COLOR_COLOR] = c4d.Vector(1, 0, 0)  # Red
            mat[c4d.MATERIAL_USE_COLOR] = True
            doc.InsertMaterial(mat)
            
            # Apply material
            texture_tag = c4d.TextureTag()
            texture_tag.SetMaterial(mat)
            cube.InsertTag(texture_tag)
            
            # Insert and track
            doc.InsertObject(cube, node)
            self.preview_objects.append(cube)
        
        c4d.EventAdd()
    
    def clear_preview(self):
        """Clear all preview objects"""
        for obj in self.preview_objects:
            if obj.GetDocument():
                obj.Remove()
        
        self.preview_objects = []
    
    def get_camera_positions(self, node):
        """Get camera positions based on current settings"""
        data = node.GetDataInstance()
        pattern = data.GetLong(self.parent_tool.ARRAY_PATTERN)
        
        if pattern == self.parent_tool.PATTERN_SPHERE:
            return self.get_sphere_positions(node)
        elif pattern == self.parent_tool.PATTERN_CYLINDER:
            return self.get_cylinder_positions(node)
        elif pattern == self.parent_tool.PATTERN_GRID:
            return self.get_grid_positions(node)
        elif pattern == self.parent_tool.PATTERN_VERTICES:
            return self.get_vertex_positions(node)
        
        return []
    
    def get_sphere_positions(self, node):
        """Get spherical array positions"""
        data = node.GetDataInstance()
        count = data.GetLong(self.parent_tool.CAMERA_COUNT)
        radius = data.GetReal(self.parent_tool.RADIUS)
        
        positions = []
        
        for i in range(count):
            golden_angle = math.pi * (3.0 - math.sqrt(5.0))
            y = 1 - (i / float(count - 1)) * 2
            radius_at_y = math.sqrt(1 - y * y)
            theta = golden_angle * i
            
            x = math.cos(theta) * radius_at_y
            z = math.sin(theta) * radius_at_y
            
            positions.append(c4d.Vector(x * radius, y * radius, z * radius))
        
        return positions
    
    def get_cylinder_positions(self, node):
        """Get cylindrical array positions"""
        data = node.GetDataInstance()
        count = data.GetLong(self.parent_tool.CAMERA_COUNT)
        radius = data.GetReal(self.parent_tool.RADIUS)
        height = data.GetReal(self.parent_tool.HEIGHT)
        
        positions = []
        
        for i in range(count):
            angle = (i / float(count)) * 2 * math.pi
            y_offset = (i % 3 - 1) * height / 6
            
            x = math.cos(angle) * radius
            z = math.sin(angle) * radius
            y = y_offset
            
            positions.append(c4d.Vector(x, y, z))
        
        return positions
    
    def get_grid_positions(self, node):
        """Get grid array positions"""
        data = node.GetDataInstance()
        size_x = data.GetLong(self.parent_tool.GRID_SIZE_X)
        size_y = data.GetLong(self.parent_tool.GRID_SIZE_Y)
        radius = data.GetReal(self.parent_tool.RADIUS)
        
        positions = []
        
        for x in range(size_x):
            for y in range(size_y):
                pos_x = (x - (size_x - 1) / 2.0) * radius
                pos_y = (y - (size_y - 1) / 2.0) * radius
                pos_z = radius
                
                positions.append(c4d.Vector(pos_x, pos_y, pos_z))
        
        return positions
    
    def get_vertex_positions(self, node):
        """Get vertex array positions"""
        doc = node.GetDocument()
        selected_obj = doc.GetActiveObject()
        
        if not selected_obj or selected_obj.GetType() != c4d.Opolygon:
            return []
        
        return selected_obj.GetAllPoints()