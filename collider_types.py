# Collider Types

COL_BOX = 'BOX'           # AABB
COL_SPHERE = 'SPHERE'     # Sphere
COL_CAPSULE = 'CAPSULE'   # Capsule
COL_CYLINDER = 'CYLINDER' # Cylinder

# Collision Type設定をBlender側で管理するためのID定義
COLLISION_TYPE_DEFAULT = 'Default'
COLLISION_TYPE_WORLD = 'World'
COLLISION_TYPE_FLOOR = 'Floor'
COLLISION_TYPE_OBSTACLE = 'Obstacle'
COLLISION_TYPE_PILLAR = 'Pillar'
COLLISION_TYPE_LADDER = 'Ladder'
COLLISION_TYPE_FENCE = 'Fence'
COLLISION_TYPE_TREE = 'Tree'
COLLISION_TYPE_LEAF = 'Leaf'
COLLISION_TYPE_WALL = 'Wall'
COLLISION_TYPE_PLATFORM = 'Platform'
COLLISION_TYPE_TRIGGER = 'Trigger'
COLLISION_TYPE_NO_COLLISION = 'NoCollision'

# Collision TypeのJSON出力用IDはC++側の追従前にBlenderツール内で固定する
COLLISION_TYPE_ID_MAP = {
    COLLISION_TYPE_DEFAULT: 0,
    COLLISION_TYPE_WORLD: 1,
    COLLISION_TYPE_FLOOR: 2,
    COLLISION_TYPE_OBSTACLE: 3,
    COLLISION_TYPE_PILLAR: 4,
    COLLISION_TYPE_LADDER: 5,
    COLLISION_TYPE_FENCE: 6,
    COLLISION_TYPE_TREE: 7,
    COLLISION_TYPE_LEAF: 8,
    COLLISION_TYPE_WALL: 9,
    COLLISION_TYPE_PLATFORM: 10,
    COLLISION_TYPE_TRIGGER: 11,
    COLLISION_TYPE_NO_COLLISION: 12,
}

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
# Collision TypeをUIのEnumPropertyで選択するための項目
def collision_type_enum_items():
    return [
        (COLLISION_TYPE_DEFAULT, "Default", "Default collision type"),
        (COLLISION_TYPE_WORLD, "World", "World collision type"),
        (COLLISION_TYPE_FLOOR, "Floor", "Floor collision type"),
        (COLLISION_TYPE_OBSTACLE, "Obstacle", "Obstacle collision type"),
        (COLLISION_TYPE_PILLAR, "Pillar", "Pillar collision type"),
        (COLLISION_TYPE_LADDER, "Ladder", "Ladder collision type"),
        (COLLISION_TYPE_FENCE, "Fence", "Fence collision type"),
        (COLLISION_TYPE_TREE, "Tree", "Tree collision type"),
        (COLLISION_TYPE_LEAF, "Leaf", "Leaf collision type"),
        (COLLISION_TYPE_WALL, "Wall", "Wall collision type"),
        (COLLISION_TYPE_PLATFORM, "Platform", "Platform collision type"),
        (COLLISION_TYPE_TRIGGER, "Trigger", "Trigger collision type"),
        (COLLISION_TYPE_NO_COLLISION, "NoCollision", "No collision type"),
    ]

# 未設定または不明なCollision TypeはDefault扱いでJSON出力する
def collision_type_id(collision_type):
    return COLLISION_TYPE_ID_MAP.get(str(collision_type), COLLISION_TYPE_ID_MAP[COLLISION_TYPE_DEFAULT])
