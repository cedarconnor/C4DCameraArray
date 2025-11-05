CONTAINER camera_array_tool
{
    NAME camera_array_tool;
    INCLUDE Obase;

    GROUP ID_OBJECTPROPERTIES
    {
        DEFAULT 1;

        GROUP
        {
            COLUMNS 2;
            
            STATICTEXT { NAME "Array Pattern:"; }
            LONG ARRAY_PATTERN
            {
                CYCLE
                {
                    PATTERN_VERTICES;
                    PATTERN_SPHERE;
                    PATTERN_CYLINDER;
                    PATTERN_GRID;
                }
            }
            
            STATICTEXT { NAME "Camera Count:"; }
            LONG CAMERA_COUNT { MIN 1; MAX 1000; }
            
            STATICTEXT { NAME "Radius:"; }
            REAL RADIUS { UNIT METER; MIN 0.1; }
            
            STATICTEXT { NAME "Height:"; }
            REAL HEIGHT { UNIT METER; }
            
            STATICTEXT { NAME "Grid Size X:"; }
            LONG GRID_SIZE_X { MIN 1; MAX 100; }
            
            STATICTEXT { NAME "Grid Size Y:"; }
            LONG GRID_SIZE_Y { MIN 1; MAX 100; }
            
            STATICTEXT { NAME "Distribution:"; }
            LONG DISTRIBUTION_METHOD
            {
                CYCLE
                {
                    DIST_GOLDEN_SPIRAL;
                    DIST_FIBONACCI;
                    DIST_HALTON;
                    DIST_POISSON;
                }
            }

            STATICTEXT { NAME "Direction:"; }
            LONG DIRECTION
            {
                CYCLE
                {
                    DIR_INWARD;
                    DIR_OUTWARD;
                    DIR_TANGENTIAL;
                    DIR_CUSTOM;
                }
            }

            STATICTEXT { NAME "Target Object:"; }
            LINK TARGET_OBJECT { ACCEPT { Obase; } }
            
            STATICTEXT { NAME "Focal Length:"; }
            REAL FOCAL_LENGTH { UNIT METER; MIN 1.0; MAX 500.0; }
            
            CHECKBOX SYNC_FOCAL_LENGTH { NAME "Sync Focal Length"; }
            CHECKBOX CREATE_TAKES { NAME "Create Takes"; }
            CHECKBOX SHOW_PREVIEW { NAME "Show Preview"; }
        }

        GROUP
        {
            COLUMNS 2;
            STATICTEXT { NAME "Batch Render"; BOLD; }
            STATICTEXT { }

            CHECKBOX BATCH_RENDER_ENABLED { NAME "Enable Batch Render"; }
            STATICTEXT { }

            STATICTEXT { NAME "Output Path:"; }
            FILENAME BATCH_RENDER_PATH { DIRECTORY; }
        }

        GROUP
        {
            COLUMNS 3;
            BUTTON CREATE_ARRAY { NAME "Create Array"; }
            BUTTON EXPORT_COLMAP { NAME "Export COLMAP"; }
            BUTTON CLEAR_CAMERAS { NAME "Clear Cameras"; }
        }

        GROUP
        {
            COLUMNS 1;
            BUTTON BATCH_RENDER { NAME "Batch Render All Cameras"; }
        }
    }
}