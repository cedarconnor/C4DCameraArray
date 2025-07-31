#pragma once

enum
{
    // Object ID
    CAMERA_ARRAY_TOOL = 1054321,
    
    // Parameters
    ARRAY_PATTERN = 1000,
    CAMERA_COUNT = 1001,
    RADIUS = 1002,
    HEIGHT = 1003,
    GRID_SIZE_X = 1004,
    GRID_SIZE_Y = 1005,
    DIRECTION = 1006,
    TARGET_OBJECT = 1007,
    FOCAL_LENGTH = 1008,
    SYNC_FOCAL_LENGTH = 1009,
    CREATE_TAKES = 1010,
    SHOW_PREVIEW = 1011,
    
    // Buttons
    CREATE_ARRAY = 1020,
    EXPORT_COLMAP = 1021,
    CLEAR_CAMERAS = 1022,
    
    // Pattern types
    PATTERN_VERTICES = 0,
    PATTERN_SPHERE = 1,
    PATTERN_CYLINDER = 2,
    PATTERN_GRID = 3,
    
    // Direction types
    DIR_INWARD = 0,
    DIR_OUTWARD = 1,
    DIR_TANGENTIAL = 2,
    DIR_CUSTOM = 3
};