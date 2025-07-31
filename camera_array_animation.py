import c4d
import math
from c4d.modules import takesystem

class CameraArrayAnimation:
    """Animation support for 4D camera arrays"""
    
    def __init__(self, parent_tool):
        self.parent_tool = parent_tool
        self.animated_cameras = []
    
    def create_animated_array(self, node, frame_range=(0, 100), frame_step=1):
        """Create animated camera array for 4D workflows"""
        doc = node.GetDocument()
        if not doc:
            return
        
        data = node.GetDataInstance()
        pattern = data.GetLong(self.parent_tool.ARRAY_PATTERN)
        
        # Get reference object for animation
        selected_obj = doc.GetActiveObject()
        if not selected_obj:
            c4d.gui.MessageDialog('Please select an object to animate around.')
            return
        
        doc.StartUndo()
        
        # Create base cameras
        base_cameras = self.parent_tool.create_camera_array(node)
        
        # Animate each camera
        for i, cam in enumerate(base_cameras):
            self.animate_camera(cam, selected_obj, frame_range, frame_step, i)
        
        self.animated_cameras = base_cameras
        
        doc.EndUndo()
        c4d.EventAdd()
        
        return base_cameras
    
    def animate_camera(self, camera, reference_obj, frame_range, frame_step, cam_index):
        """Animate a single camera around reference object"""
        doc = camera.GetDocument()
        
        # Create tracks for position and rotation
        pos_track = c4d.CTrack(camera, c4d.ID_BASEOBJECT_POSITION)
        rot_track = c4d.CTrack(camera, c4d.ID_BASEOBJECT_ROTATION)
        
        camera.InsertTrackSorted(pos_track)
        camera.InsertTrackSorted(rot_track)
        
        pos_curve = pos_track.GetCurve()
        rot_curve = rot_track.GetCurve()
        
        # Animate over frame range
        for frame in range(frame_range[0], frame_range[1] + 1, frame_step):
            time = c4d.BaseTime(frame, doc.GetFps())
            
            # Calculate animated position (orbital motion)
            angle_offset = (cam_index / len(self.animated_cameras)) * 2 * math.pi
            orbit_angle = (frame / float(frame_range[1] - frame_range[0])) * 2 * math.pi + angle_offset
            
            # Get reference object position (could be animated)
            ref_pos = reference_obj.GetAbsPos() if reference_obj else c4d.Vector(0, 0, 0)
            
            # Calculate orbital position
            radius = 200.0  # Could be parameter
            orbit_x = math.cos(orbit_angle) * radius
            orbit_z = math.sin(orbit_angle) * radius
            orbit_y = math.sin(frame / 30.0) * 50.0  # Vertical oscillation
            
            animated_pos = ref_pos + c4d.Vector(orbit_x, orbit_y, orbit_z)
            
            # Calculate look-at rotation
            direction = (ref_pos - animated_pos).GetNormalized()
            up_vector = c4d.Vector(0, 1, 0)
            right_vector = up_vector.Cross(direction).GetNormalized()
            
            if right_vector.GetLength() < 0.001:
                right_vector = c4d.Vector(1, 0, 0)
                up_vector = direction.Cross(right_vector).GetNormalized()
            else:
                up_vector = direction.Cross(right_vector).GetNormalized()
            
            # Convert to HPB rotation
            matrix = c4d.Matrix(animated_pos, right_vector, up_vector, direction)
            rotation = c4d.utils.MatrixToHPB(matrix, c4d.ROTATIONORDER_HPB)
            
            # Add keyframes
            pos_key = pos_curve.AddKey(time)
            pos_key['value'] = animated_pos
            pos_key.SetInterpolation(pos_curve, c4d.CINTERPOLATION_SPLINE)
            
            rot_key = rot_curve.AddKey(time)
            rot_key['value'] = rotation
            rot_key.SetInterpolation(rot_curve, c4d.CINTERPOLATION_SPLINE)
    
    def create_4d_gaussian_setup(self, node):
        """Create setup optimized for 4D Gaussian Splatting"""
        doc = node.GetDocument()
        if not doc:
            return
        
        # Create temporal camera array with specific timing
        frame_count = 120  # 4 seconds at 30fps
        camera_count = 8   # Fewer cameras for temporal coherence
        
        cameras = []
        
        # Create cameras with temporal offset
        for i in range(camera_count):
            # Create base camera
            cam = c4d.BaseObject(c4d.Ocamera)
            cam.SetName(f'4DGS_Cam_{i+1}')
            
            # Position in sphere
            angle = (i / float(camera_count)) * 2 * math.pi
            radius = 300.0
            pos = c4d.Vector(
                math.cos(angle) * radius,
                0,
                math.sin(angle) * radius
            )
            cam.SetAbsPos(pos)
            
            # Orient toward center
            direction = (c4d.Vector(0, 0, 0) - pos).GetNormalized()
            self.parent_tool.orient_camera_to_direction(cam, direction)
            
            # Add temporal animation (slight movement for 4D)
            self.add_temporal_animation(cam, i, frame_count)
            
            doc.InsertObject(cam, node)
            cameras.append(cam)
        
        return cameras
    
    def add_temporal_animation(self, camera, cam_index, frame_count):
        """Add subtle temporal animation for 4D capture"""
        doc = camera.GetDocument()
        
        # Create position track for subtle movement
        pos_track = c4d.CTrack(camera, c4d.ID_BASEOBJECT_POSITION)
        camera.InsertTrackSorted(pos_track)
        pos_curve = pos_track.GetCurve()
        
        base_pos = camera.GetAbsPos()
        
        # Add keyframes with subtle movement
        for frame in range(0, frame_count + 1, 5):  # Every 5 frames
            time = c4d.BaseTime(frame, doc.GetFps())
            
            # Subtle oscillation
            offset_scale = 10.0  # Small movement
            time_factor = frame / float(frame_count)
            
            offset = c4d.Vector(
                math.sin(time_factor * 2 * math.pi + cam_index) * offset_scale,
                math.cos(time_factor * 3 * math.pi + cam_index) * offset_scale * 0.5,
                math.sin(time_factor * 1.5 * math.pi + cam_index) * offset_scale * 0.3
            )
            
            animated_pos = base_pos + offset
            
            key = pos_curve.AddKey(time)
            key['value'] = animated_pos
            key.SetInterpolation(pos_curve, c4d.CINTERPOLATION_SPLINE)
    
    def export_4d_sequence(self, node, output_dir):
        """Export 4D camera sequence for training"""
        if not self.animated_cameras:
            c4d.gui.MessageDialog('No animated cameras to export.')
            return
        
        doc = node.GetDocument()
        frame_range = (0, 100)  # Could be parameter
        
        # Export camera parameters for each frame
        sequence_data = {
            'cameras': [],
            'frames': [],
            'metadata': {
                'fps': doc.GetFps(),
                'frame_range': frame_range,
                'camera_count': len(self.animated_cameras)
            }
        }
        
        for frame in range(frame_range[0], frame_range[1] + 1):
            time = c4d.BaseTime(frame, doc.GetFps())
            doc.SetTime(time)
            doc.ExecutePasses(None, True, True, True, c4d.BUILDFLAGS_NONE)
            
            frame_data = {
                'frame': frame,
                'time': float(time.Get()),
                'cameras': []
            }
            
            for i, cam in enumerate(self.animated_cameras):
                mg = cam.GetMg()
                pos = mg.off
                
                # Get FOV
                fov = cam[c4d.CAMERAOBJECT_FOV]
                
                cam_data = {
                    'id': i,
                    'name': cam.GetName(),
                    'position': [pos.x, pos.y, pos.z],
                    'rotation_matrix': [
                        [mg.v1.x, mg.v1.y, mg.v1.z],
                        [mg.v2.x, mg.v2.y, mg.v2.z],
                        [mg.v3.x, mg.v3.y, mg.v3.z]
                    ],
                    'fov': math.degrees(fov)
                }
                
                frame_data['cameras'].append(cam_data)
            
            sequence_data['frames'].append(frame_data)
        
        # Save sequence data
        import json
        import os
        
        output_file = os.path.join(output_dir, '4d_camera_sequence.json')
        with open(output_file, 'w') as f:
            json.dump(sequence_data, f, indent=2)
        
        c4d.gui.MessageDialog(f'4D sequence exported to {output_file}')
    
    def clear_animation(self):
        """Clear all animated cameras"""
        for cam in self.animated_cameras:
            if cam.GetDocument():
                cam.Remove()
        
        self.animated_cameras = []