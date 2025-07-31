# Advanced Camera Array Tool for Cinema 4D

A comprehensive Camera Array plugin for Cinema 4D that creates multiple camera perspectives for 3D visualization, photogrammetry, and Gaussian Splatting workflows.

## Features

### 🎥 Multiple Array Patterns
- **Vertex Array**: Create cameras at polygon vertices
- **Spherical Array**: Golden spiral distribution for optimal coverage
- **Cylindrical Array**: Cameras arranged in cylindrical formation
- **Grid Array**: Rectangular grid camera placement

### 🎯 Advanced Camera Control
- **Direction Options**: Inward, outward, tangential, or custom camera orientations
- **Target Tracking**: Point cameras at specific objects
- **Focal Length Sync**: Synchronize focal length across all cameras
- **Take System Integration**: Automatic camera take creation

### 📤 Export Capabilities
- **COLMAP Export**: Generate camera.txt and images.txt for photogrammetry
- **Camera Metadata**: Complete camera parameter export (JSON)
- **4D Sequences**: Animated camera data for temporal reconstruction

### 🎬 Animation Support
- **4D Gaussian Splatting**: Optimized camera sequences for 4DGS training
- **Temporal Animation**: Automated camera movement for time-based capture
- **Orbital Motion**: Smart camera path generation

### ⚡ Performance Optimizations
- **Smart Distribution**: Fibonacci sphere, Halton sequence, Poisson disk sampling
- **Occlusion Culling**: Remove cameras with poor visibility
- **Overlap Prevention**: Maintain minimum camera distances
- **Real-time Preview**: Visualize camera placement before creation

## Installation

1. Copy the entire `C4DCameraArray` folder to your Cinema 4D plugins directory:
   - Windows: `C:\Program Files\Maxon Cinema 4D [Version]\plugins\`
   - Mac: `/Applications/Maxon Cinema 4D [Version]/plugins/`

2. Register the plugin by getting an official Plugin ID from Plugin Cafe

3. Restart Cinema 4D

## Example Files

The repository includes:
- **`Splat.mp4`**: Example Gaussian Splatting result showcasing the quality achievable with this camera array tool

## Quick Start

### Basic Usage
1. Create or select a polygon object in your scene
2. Add the **Camera Array Tool** object from the plugins menu
3. Configure your desired array pattern and settings
4. Click **Create Array** to generate cameras
5. Use **Export COLMAP** for photogrammetry workflows

### Example Results
See `Splat.mp4` for an example of Gaussian Splatting results created using this camera array tool. The video demonstrates the quality achievable with properly positioned camera arrays for 3D reconstruction workflows.

### Array Patterns

#### Spherical Array
- **Use Case**: 360° object capture, optimal coverage
- **Parameters**: Camera count, radius
- **Best For**: Product visualization, object scanning

#### Cylindrical Array  
- **Use Case**: Tall objects, architectural elements
- **Parameters**: Camera count, radius, height
- **Best For**: Building facades, sculptures

#### Grid Array
- **Use Case**: Planar capture, facade photography
- **Parameters**: Grid size X/Y, spacing
- **Best For**: Flat surfaces, texture capture

#### Vertex Array
- **Use Case**: Custom placement based on geometry
- **Parameters**: Uses selected polygon object vertices
- **Best For**: Irregular shapes, artistic arrangements

### Camera Directions

- **Inward**: Cameras point toward target (default: world origin)
- **Outward**: Cameras point away from target
- **Tangential**: Cameras oriented tangent to sphere
- **Custom**: Manual direction control

## Advanced Workflows

### Gaussian Splatting Preparation
1. Set array pattern to **Spherical** with 50-100 cameras
2. Set direction to **Inward** targeting your object
3. Enable **Sync Focal Length** (35mm recommended)
4. Click **Export COLMAP** to generate training data
5. Use exported files with Gaussian Splatting training pipelines

**Result Example**: See `Splat.mp4` for a demonstration of the quality achievable with proper camera array positioning using this tool.

### 4D Gaussian Splatting
1. Use the animation system to create temporal camera sequences
2. Export 4D sequence data for training
3. Supports object animation and camera movement

### Photogrammetry Workflow
1. Create spherical array around your object
2. Ensure good coverage (50+ cameras recommended)
3. Export COLMAP data
4. Import into photogrammetry software (Meshroom, Reality Capture, etc.)

## Parameters Reference

### Array Settings
- **Array Pattern**: Choose distribution method
- **Camera Count**: Number of cameras (1-1000)
- **Radius**: Distance from center/spacing
- **Height**: Cylinder height parameter
- **Grid Size X/Y**: Grid dimensions

### Camera Settings
- **Direction**: Camera orientation method
- **Target Object**: Object to point cameras toward
- **Focal Length**: Camera focal length (mm)
- **Sync Focal Length**: Apply same focal length to all cameras

### Workflow Options
- **Create Takes**: Automatically create take for each camera
- **Show Preview**: Display camera position preview

## Export Formats

### COLMAP Format
- `cameras.txt`: Camera intrinsic parameters
- `images.txt`: Camera poses and orientations
- Compatible with SfM pipelines

### JSON Metadata
- Complete camera parameters
- Position, rotation matrices
- Intrinsic calibration data
- Render settings

## Performance Tips

1. **Start Small**: Test with fewer cameras first
2. **Use Preview**: Enable preview to verify placement
3. **Optimize Distribution**: Tool automatically prevents overlaps
4. **Memory Management**: Clear unused cameras regularly

## Compatibility

- Cinema 4D R20+
- Windows 10/11, macOS 10.14+
- Python 3.x support
- Take System integration

## Troubleshooting

### Common Issues
- **"No cameras created"**: Ensure valid polygon object is selected for vertex mode
- **Cameras overlapping**: Increase radius or use optimization features
- **Export failed**: Check file permissions and disk space
- **Take creation failed**: Ensure Take System is available in document

### Performance Issues
- Reduce camera count for complex scenes
- Use preview mode to test settings
- Clear preview objects when not needed

## Technical Details

### Camera Distribution Algorithms
- **Golden Spiral**: Even angular distribution
- **Fibonacci Sphere**: Optimal sphere packing
- **Halton Sequence**: Low-discrepancy sampling
- **Poisson Disk**: Uniform spatial distribution

### Coordinate Systems
- Cinema 4D standard coordinate system
- COLMAP format conversion included
- Quaternion rotation support

## Contributing

This plugin is designed for defensive security and 3D visualization purposes only. 
Contributions welcome for:
- Additional array patterns
- Export format support
- Performance improvements
- Documentation enhancements

## License

Educational and research use. Commercial licensing available.

## Changelog

### v2.0.0 (Current)
- Complete rewrite with advanced features
- Multiple array patterns
- COLMAP export support
- 4D animation workflows
- Performance optimizations
- Preview system

### v1.0.0 (Original)
- Basic vertex-based camera creation
- Take system integration
