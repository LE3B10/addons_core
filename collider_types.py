# Collider Types

COL_BOX = 'BOX'           # AABB
COL_SPHERE = 'SPHERE'     # Sphere
COL_CAPSULE = 'CAPSULE'   # Capsule
COL_CYLINDER = 'CYLINDER' # Cylinder

All_TYPES = {
    COL_BOX,
    COL_SPHERE,
    COL_CAPSULE,
    COL_CYLINDER,
}

def enum_items():
    return[
        (COL_BOX, "Box", "AABB"),
        (COL_SPHERE, "Sphere", "Sphere"),
        (COL_CAPSULE, "Capsule", "Capsule"),
        (COL_CYLINDER, "Cylinder", "Cylinder"),
    ]