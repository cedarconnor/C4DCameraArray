import c4d
import math
import json
import os

class CameraArrayUtils:
    """Utility functions for camera array optimization and management"""
    
    @staticmethod
    def optimize_camera_distribution(positions, min_distance=50.0):
        """Optimize camera positions to avoid overlaps and ensure minimum distance"""
        optimized_positions = []
        
        for pos in positions:
            adjusted_pos = pos
            
            # Check distance to all previously added positions
            while True:
                too_close = False
                
                for existing_pos in optimized_positions:
                    distance = (adjusted_pos - existing_pos).GetLength()
                    if distance < min_distance:
                        # Move away from existing position
                        direction = (adjusted_pos - existing_pos).GetNormalized()
                        adjusted_pos = existing_pos + direction * min_distance
                        too_close = True
                        break
                
                if not too_close:
                    break
            
            optimized_positions.append(adjusted_pos)
        
        return optimized_positions
    
    @staticmethod
    def calculate_coverage_score(positions, target_center=None):
        """Calculate how well the camera positions cover the target"""
        if not positions:
            return 0.0
        
        if target_center is None:
            target_center = c4d.Vector(0, 0, 0)
        
        # Calculate angular coverage
        angles = []
        for pos in positions:
            direction = (pos - target_center).GetNormalized()
            # Convert to spherical coordinates
            theta = math.atan2(direction.z, direction.x)  # Azimuth
            phi = math.asin(direction.y)  # Elevation
            angles.append((theta, phi))
        
        # Simple coverage metric based on angular spread
        theta_range = max(angles, key=lambda x: x[0])[0] - min(angles, key=lambda x: x[0])[0]
        phi_range = max(angles, key=lambda x: x[1])[1] - min(angles, key=lambda x: x[1])[1]
        
        # Normalize to 0-1 range
        coverage = (theta_range / (2 * math.pi)) * (phi_range / math.pi)
        return min(coverage, 1.0)
    
    @staticmethod
    def cull_occluded_cameras(cameras, target_obj, occlusion_threshold=0.8):
        """Remove cameras that would be heavily occluded"""
        if not target_obj or not cameras:
            return cameras
        
        visible_cameras = []
        doc = cameras[0].GetDocument()
        
        for cam in cameras:
            # Simple occlusion test using ray casting
            cam_pos = cam.GetAbsPos()
            target_pos = target_obj.GetAbsPos()
            
            # Cast ray from camera to target
            ray_direction = (target_pos - cam_pos).GetNormalized()
            ray_length = (target_pos - cam_pos).GetLength()
            
            # Simple visibility test (in production, use proper ray casting)
            occlusion_score = CameraArrayUtils.calculate_occlusion_score(
                cam_pos, target_pos, target_obj, doc
            )
            
            if occlusion_score < occlusion_threshold:
                visible_cameras.append(cam)
        
        return visible_cameras
    
    @staticmethod
    def calculate_occlusion_score(cam_pos, target_pos, target_obj, doc):
        """Calculate occlusion score between camera and target"""
        # Simplified occlusion calculation
        # In production, use proper ray-object intersection
        
        direction = (target_pos - cam_pos).GetNormalized()
        distance = (target_pos - cam_pos).GetLength()
        
        # Sample points along the ray
        sample_count = 10
        occluded_samples = 0
        
        for i in range(1, sample_count):
            t = i / float(sample_count)
            sample_pos = cam_pos + direction * distance * t
            
            # Check if sample point is inside any geometry
            # This is a simplified check - real implementation would use proper collision detection
            if CameraArrayUtils.point_inside_bounds(sample_pos, target_obj):
                occluded_samples += 1
        
        return occluded_samples / float(sample_count - 1)
    
    @staticmethod
    def point_inside_bounds(point, obj):
        """Check if point is inside object bounds (simplified)"""
        if not obj:
            return False
        
        # Get object bounding box
        obj_mg = obj.GetMg()
        obj_pos = obj_mg.off
        
        # Simple bounding sphere test
        if obj.GetType() == c4d.Opolygon:
            # Get approximate radius from bounding box
            bbox = obj.GetRad()
            max_radius = max(bbox.x, bbox.y, bbox.z)
            distance = (point - obj_pos).GetLength()
            return distance < max_radius * 0.8  # 80% of bounding radius
        
        return False
    
    @staticmethod
    def generate_smart_distribution(count, pattern_type, radius, target_obj=None):
        """Generate optimized camera distribution using smart algorithms"""
        positions = []
        
        if pattern_type == "fibonacci_sphere":
            positions = CameraArrayUtils.fibonacci_sphere_distribution(count, radius)
        elif pattern_type == "halton_sequence":
            positions = CameraArrayUtils.halton_sequence_distribution(count, radius)
        elif pattern_type == "poisson_disk":
            positions = CameraArrayUtils.poisson_disk_distribution(count, radius)
        else:
            # Default to golden spiral
            positions = CameraArrayUtils.golden_spiral_distribution(count, radius)
        
        # Optimize distribution
        positions = CameraArrayUtils.optimize_camera_distribution(positions)
        
        return positions
    
    @staticmethod
    def fibonacci_sphere_distribution(count, radius):
        """Generate Fibonacci sphere distribution for optimal spacing"""
        positions = []
        
        for i in range(count):
            # Fibonacci spiral
            y = 1 - (i / float(count - 1)) * 2  # y goes from 1 to -1
            radius_at_y = math.sqrt(1 - y * y)
            
            # Golden angle
            golden_angle = math.pi * (3.0 - math.sqrt(5.0))
            theta = golden_angle * i
            
            x = math.cos(theta) * radius_at_y
            z = math.sin(theta) * radius_at_y
            
            positions.append(c4d.Vector(x * radius, y * radius, z * radius))
        
        return positions
    
    @staticmethod
    def halton_sequence_distribution(count, radius):
        """Generate Halton sequence distribution for low-discrepancy sampling"""
        positions = []
        
        def halton_sequence(index, base):
            result = 0.0
            f = 1.0 / base
            i = index
            while i > 0:
                result += f * (i % base)
                i //= base
                f /= base
            return result
        
        for i in range(count):
            # Use Halton sequence for spherical coordinates
            u = halton_sequence(i, 2)
            v = halton_sequence(i, 3)
            
            # Convert to spherical coordinates
            theta = 2 * math.pi * u
            phi = math.acos(2 * v - 1)
            
            # Convert to Cartesian
            x = radius * math.sin(phi) * math.cos(theta)
            y = radius * math.cos(phi)
            z = radius * math.sin(phi) * math.sin(theta)
            
            positions.append(c4d.Vector(x, y, z))
        
        return positions
    
    @staticmethod
    def poisson_disk_distribution(count, radius):
        """Generate Poisson disk distribution for uniform spacing"""
        # Simplified 2D Poisson disk sampling projected onto sphere
        positions = []
        max_attempts = 30
        min_distance = radius * 0.3
        
        # Start with random point
        if count > 0:
            angle = 0
            pos = c4d.Vector(radius, 0, 0)
            positions.append(pos)
        
        while len(positions) < count:
            # Try to place new point
            placed = False
            
            for attempt in range(max_attempts):
                # Random spherical coordinates
                theta = 2 * math.pi * (attempt / float(max_attempts))
                phi = math.pi * (len(positions) / float(count))
                
                x = radius * math.sin(phi) * math.cos(theta)
                y = radius * math.cos(phi)
                z = radius * math.sin(phi) * math.sin(theta)
                
                candidate = c4d.Vector(x, y, z)
                
                # Check minimum distance
                valid = True
                for existing in positions:
                    if (candidate - existing).GetLength() < min_distance:
                        valid = False
                        break
                
                if valid:
                    positions.append(candidate)
                    placed = True
                    break
            
            if not placed:
                # Fallback to simple angular distribution
                angle = len(positions) * 2.4  # Approximately golden angle
                y = (len(positions) / float(count)) * 2 - 1
                radius_at_y = math.sqrt(1 - y * y)
                
                x = math.cos(angle) * radius_at_y * radius
                z = math.sin(angle) * radius_at_y * radius
                
                positions.append(c4d.Vector(x, y * radius, z))
        
        return positions
    
    @staticmethod
    def golden_spiral_distribution(count, radius):
        """Generate golden spiral distribution"""
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
    
    @staticmethod
    def export_camera_metadata(cameras, filepath):
        """Export comprehensive camera metadata"""
        metadata = {
            'version': '1.0',
            'camera_count': len(cameras),
            'export_time': str(c4d.GeGetCurrentTime()),
            'cameras': []
        }
        
        for i, cam in enumerate(cameras):
            if not cam or not cam.GetDocument():
                continue
            
            # Get camera properties
            mg = cam.GetMg()
            pos = mg.off
            
            # Get FOV and other camera parameters
            fov = cam.get(c4d.CAMERAOBJECT_FOV, math.radians(35.0))
            focal_length = cam.get(c4d.CAMERAOBJECT_FOCUS, 35.0)
            
            # Get render resolution
            doc = cam.GetDocument()
            rd = doc.GetActiveRenderData()
            width = rd[c4d.RDATA_XRES]
            height = rd[c4d.RDATA_YRES]
            
            cam_data = {
                'id': i,
                'name': cam.GetName(),
                'position': [pos.x, pos.y, pos.z],
                'rotation_matrix': [
                    [mg.v1.x, mg.v1.y, mg.v1.z],
                    [mg.v2.x, mg.v2.y, mg.v2.z],
                    [mg.v3.x, mg.v3.y, mg.v3.z]
                ],
                'fov_radians': fov,
                'fov_degrees': math.degrees(fov),
                'focal_length': focal_length,
                'resolution': [width, height],
                'intrinsics': {
                    'fx': width / (2.0 * math.tan(fov / 2.0)),
                    'fy': height / (2.0 * math.tan(fov / 2.0)),
                    'cx': width / 2.0,
                    'cy': height / 2.0
                }
            }
            
            metadata['cameras'].append(cam_data)
        
        # Save metadata
        with open(filepath, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return filepath