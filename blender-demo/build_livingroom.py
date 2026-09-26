import bpy, math, random
from mathutils import Vector, Matrix

random.seed(7)
D = math.radians

# ---------- 场景重置 ----------
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# ---------- 材质 ----------
def make_mat(name, color, rough=0.6):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    return m

MAT_MAIN  = make_mat("white_main",  (0.87, 0.87, 0.86), 0.55)
MAT_SOFT  = make_mat("white_fabric",(0.90, 0.90, 0.89), 0.9)
MAT_CERAM = make_mat("white_gloss", (0.93, 0.93, 0.92), 0.15)
MAT_LEAF  = make_mat("white_leaf",  (0.80, 0.80, 0.78), 0.7)
MAT_DEEP  = make_mat("white_deep",  (0.72, 0.72, 0.71), 0.5)   # 画芯/缝隙等略深

def set_mat(obj, mat=MAT_MAIN):
    obj.data.materials.append(mat)

# ---------- 基础工具 ----------
def box(name, size, loc, rot=(0,0,0), mat=MAT_MAIN, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.active_object
    o.name = name
    o.scale = (size[0], size[1], size[2])
    if bevel > 0:
        m = o.modifiers.new("bevel", 'BEVEL')
        m.width = bevel
        m.segments = 4
    set_mat(o, mat)
    return o

def cyl(name, r, depth, loc, rot=(0,0,0), mat=MAT_MAIN, verts=32, bevel=0.0):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, vertices=verts,
                                        location=loc, rotation=rot)
    o = bpy.context.active_object
    o.name = name
    if bevel > 0:
        m = o.modifiers.new("bevel", 'BEVEL')
        m.width = bevel
        m.segments = 3
    set_mat(o, mat)
    return o

def sphere(name, r, loc, scale=(1,1,1), mat=MAT_MAIN, sub=2):
    bpy.ops.mesh.primitive_ico_sphere_add(radius=r, subdivisions=sub, location=loc)
    o = bpy.context.active_object
    o.name = name
    o.scale = scale
    set_mat(o, mat)
    return o

def cone(name, r1, r2, depth, loc, rot=(0,0,0), mat=MAT_MAIN):
    bpy.ops.mesh.primitive_cone_add(radius1=r1, radius2=r2, depth=depth,
                                    location=loc, rotation=rot)
    o = bpy.context.active_object
    o.name = name
    set_mat(o, mat)
    return o

objs = []
def reg(*os_):
    objs.extend(os_)
    return os_[0] if len(os_) == 1 else os_

# =========================================================
# 1. 结构：地板 / 三面墙 / 天花（7m x 5m, 层高 2.8m）
# =========================================================
reg(box("floor", (7.3, 5.3, 0.1), (0, 0, -0.05), bevel=0.005))

WALL_T = 0.15
# 后墙（+Y，电视墙）
reg(box("wall_back", (7.3, WALL_T, 2.8), (0, 2.575, 1.4)))
# 右墙（+X）
reg(box("wall_right", (WALL_T, 5.3, 2.8), (3.575, 0, 1.4)))
# 前墙（-Y，挡视线外杂光）
reg(box("wall_front", (7.3, WALL_T, 2.8), (0, -2.575, 1.4)))
# 左墙（-X）拼出大窗洞：洞 y∈[-1.2,1.2], z∈[0.9,2.3]
X = -3.575
reg(box("wall_L_a", (WALL_T, 1.3, 2.8), (X, -1.85, 1.4)))
reg(box("wall_L_b", (WALL_T, 1.3, 2.8), (X,  1.85, 1.4)))
reg(box("wall_L_sill", (WALL_T, 2.4, 0.9), (X, 0, 0.45)))
reg(box("wall_L_head", (WALL_T, 2.4, 0.5), (X, 0, 2.55)))
# 天花
reg(box("ceiling", (7.3, 5.3, 0.1), (0, 0, 2.85)))

# 窗框 + 中梃（把大窗分 4 格，统一贴墙内面避免深缝）
FR = 0.05
FRX = X + 0.115
reg(box("win_frame_l", (0.07, 2.5, FR), (FRX, 0, 1.6)))
reg(box("win_frame_r", (0.07, 2.5, FR), (FRX, 0, 0.925)))   # 下横梃（窗台边）
reg(box("win_frame_t", (0.07, 2.5, FR), (FRX, 0, 2.275)))   # 上横梃
reg(box("win_mullion_v", (0.05, 0.05, 1.4), (FRX+0.008, 0, 1.6)))
reg(box("win_mullion_h", (0.05, 2.4, 0.08), (FRX+0.008, 0, 1.6)))
# 窗台板（探出墙面）
reg(box("sill_board", (0.28, 2.7, 0.035), (X+0.20, 0, 0.9175), bevel=0.012))

# 踢脚线（后墙 / 右墙 / 左墙通长）
reg(box("skirt_back", (7.0, 0.018, 0.1), (0, 2.49, 0.05)))
reg(box("skirt_right", (0.018, 5.0, 0.1), (3.49, 0, 0.05)))
reg(box("skirt_left", (0.018, 4.7, 0.1), (-3.49, 0, 0.05)))
# 顶角石膏线（后 / 右 / 左）
reg(box("cornice_back", (7.0, 0.05, 0.07), (0, 2.465, 2.765)))
reg(box("cornice_right", (0.05, 5.0, 0.07), (3.465, 0, 2.765)))
reg(box("cornice_left", (0.05, 4.7, 0.07), (-3.465, 0, 2.765)))

# 后墙房门（装饰门 + 门套 + 把手）
reg(box("door", (0.92, 0.045, 2.06), (-2.3, 2.545, 1.03), bevel=0.008))
reg(box("door_frame_l", (0.07, 0.03, 2.12), (-2.795, 2.53, 1.06)))
reg(box("door_frame_r", (0.07, 0.03, 2.12), (-1.805, 2.53, 1.06)))
reg(box("door_frame_t", (1.06, 0.03, 0.07), (-2.3, 2.53, 2.10)))
cyl("door_knob", 0.022, 0.09, (-1.95, 2.50, 1.02), rot=(D(90), 0, 0))

# =========================================================
# 2. 地毯
# =========================================================
rug = box("rug", (3.5, 2.5, 0.02), (0.15, 0.75, 0.012), mat=MAT_SOFT, bevel=0.008)

# =========================================================
# 3. 三人沙发（面向 +Y 电视墙）
# =========================================================
SX, SY = -0.25, 0.1
legs = []
for dx in (-0.95, 0.95):
    for dy in (-0.32, 0.32):
        legs.append(cyl(f"sofa_leg_{dx}_{dy}", 0.03, 0.09, (SX+dx, SY+dy, 0.045)))
reg(legs)
reg(box("sofa_base", (2.25, 0.95, 0.32), (SX, SY, 0.25), bevel=0.05))
reg(box("sofa_back", (2.25, 0.28, 0.52), (SX, SY-0.335, 0.67), bevel=0.06))
arm_l = box("sofa_arm_l", (0.28, 0.95, 0.58), (SX-1.12, SY, 0.47), bevel=0.08)
arm_r = box("sofa_arm_r", (0.28, 0.95, 0.58), (SX+1.12, SY, 0.47), bevel=0.08)
reg(arm_l, arm_r)
cushions = []
for i, dx in enumerate((-0.75, -0.02, 0.71)):
    cushions.append(box(f"seat_cushion_{i}", (0.68, 0.62, 0.17),
                        (SX+dx, SY+0.09, 0.485), bevel=0.07, mat=MAT_SOFT))
reg(cushions)
# 靠枕（随机微转）
pillows = []
px = [-0.92, -0.42, 0.18, 0.68]
for i, dx in enumerate(px):
    rz = random.uniform(-0.12, 0.12)
    pillows.append(box(f"pillow_{i}", (0.42, 0.16, 0.42),
                       (SX+dx, SY-0.18, 0.82), rot=(D(-78)+rz, 0, rz),
                       bevel=0.09, mat=MAT_SOFT))
reg(pillows)

# =========================================================
# 4. 茶几 + 桌面小物
# =========================================================
TX, TY = 0.1, 1.45
reg(box("coffee_top", (1.15, 0.62, 0.04), (TX, TY, 0.42), bevel=0.012))
reg(box("coffee_low", (0.95, 0.5, 0.025), (TX, TY, 0.16), bevel=0.008))
for dx in (-0.51, 0.51):
    for dy in (-0.25, 0.25):
        reg(box(f"coffee_leg_{dx}_{dy}", (0.035, 0.035, 0.40),
                (TX+dx, TY+dy, 0.21), bevel=0.004))
# 书堆
for i, (w, dpath, rotz) in enumerate([(0.26, 0.19, 0.05), (0.24, 0.17, -0.08), (0.21, 0.15, 0.12)]):
    reg(box(f"book_stack_{i}", (w, dpath, 0.028),
            (TX+0.32, TY-0.05, 0.455+0.03*i), rot=(0, 0, rotz), mat=MAT_DEEP))
# 陶瓷花瓶（三段）
reg(cone("vase_body", 0.055, 0.028, 0.13, (TX-0.28, TY+0.05, 0.495), mat=MAT_CERAM))
reg(cyl("vase_neck", 0.024, 0.07, (TX-0.28, TY+0.05, 0.585), mat=MAT_CERAM))
# 托盘 + 小碗
reg(cyl("tray", 0.11, 0.014, (TX-0.02, TY+0.1, 0.447), mat=MAT_DEEP))
reg(cone("bowl", 0.06, 0.04, 0.05, (TX-0.02, TY+0.1, 0.478), mat=MAT_CERAM))

# =========================================================
# 5. 电视柜 + 挂壁电视
# =========================================================
reg(box("tv_cabinet", (1.9, 0.42, 0.42), (0.3, 2.32, 0.27), bevel=0.015))
for i, dx in enumerate((-0.46, 0.46)):
    reg(box(f"cabinet_door_{i}", (0.86, 0.018, 0.32), (0.3+dx, 2.105, 0.27), bevel=0.005))
for dx in (-0.8, 0.8):
    reg(cyl(f"cab_leg_{dx}", 0.02, 0.08, (0.3+dx, 2.32, 0.04)))
reg(box("tv", (1.45, 0.045, 0.84), (0.3, 2.535, 1.5), bevel=0.006, mat=MAT_DEEP))
reg(box("tv_stand_bar", (0.5, 0.02, 0.03), (0.3, 2.51, 1.03)))

# =========================================================
# 6. 单人扶手椅（斜放右前区，整体旋转 130°）
# =========================================================
chair_parts = []
def cbox(name, size, loc, rot=(0,0,0), bevel=0.05, mat=MAT_SOFT):
    chair_parts.append(box(name, size, loc, rot, mat=mat, bevel=bevel))
cbox("armchair_seat", (0.62, 0.60, 0.14), (0, 0, 0.44))
cbox("armchair_base", (0.58, 0.56, 0.18), (0, 0, 0.28), bevel=0.03, mat=MAT_MAIN)
cbox("armchair_back", (0.62, 0.14, 0.62), (0, -0.26, 0.72), bevel=0.07)
cbox("armchair_arm_l", (0.13, 0.58, 0.34), (-0.315, 0.02, 0.62), bevel=0.06)
cbox("armchair_arm_r", (0.13, 0.58, 0.34), ( 0.315, 0.02, 0.62), bevel=0.06)
cbox("armchair_pillow", (0.34, 0.12, 0.34), (0, -0.17, 0.80), rot=(D(-72), 0, 0.05), bevel=0.08)
for dx in (-0.24, 0.24):
    for dy in (-0.22, 0.22):
        chair_parts.append(cyl(f"chair_leg_{dx}_{dy}", 0.022, 0.36, (dx, dy, 0.18),
                               rot=(D(6)*dx, D(-6)*dy, 0)))
M = Matrix.Translation((2.45, 1.55, 0)) @ Matrix.Rotation(D(130), 4, 'Z')
for o in chair_parts:
    o.matrix_world = M @ o.matrix_world
reg(chair_parts)
# 脚凳
reg(box("ottoman", (0.5, 0.42, 0.3), (1.95, 0.85, 0.17), rot=(0, 0, D(20)), bevel=0.07, mat=MAT_SOFT))

# =========================================================
# 7. 边几（沙发右端）
# =========================================================
reg(cyl("side_top", 0.24, 0.03, (1.15, 0.25, 0.56)))
reg(cyl("side_pole", 0.025, 0.54, (1.15, 0.25, 0.28)))
reg(cyl("side_base", 0.17, 0.025, (1.15, 0.25, 0.014)))

# =========================================================
# 8. 书架墙（右墙）+ 一架子的书
# =========================================================
BX, BY = 3.30, -0.7     # 背板贴右墙，架体朝 -X
W_, D_, H_ = 1.7, 0.34, 2.15
reg(box("shelf_back", (0.03, W_, H_), (BX+D_/2, BY, H_/2)))
reg(box("shelf_side_a", (D_, 0.04, H_), (BX, BY-W_/2+0.02, H_/2)))
reg(box("shelf_side_b", (D_, 0.04, H_), (BX, BY+W_/2-0.02, H_/2)))
reg(box("shelf_top", (D_, W_, 0.04), (BX, BY, H_-0.02)))
reg(box("shelf_bottom", (D_, W_, 0.04), (BX, BY, 0.06)))
levels = [0.42, 0.82, 1.22, 1.62]
for i, z in enumerate(levels):
    reg(box(f"shelf_board_{i}", (D_-0.02, W_-0.08, 0.03), (BX-0.01, BY, z)))
# 每层塞书：竖排 + 一小摞平放
for i, z in enumerate(levels):
    y = BY - W_/2 + 0.12
    while y < BY + W_/2 - 0.30:
        h = random.uniform(0.17, 0.24)
        t = random.uniform(0.018, 0.042)
        lean = random.choice([0, 0, 0, D(6)])
        reg(box(f"book_{i}_{y:.2f}", (random.uniform(0.14, 0.2), t, h),
                (BX-0.01, y, z+0.015+h/2), rot=(0, -lean, 0), mat=MAT_MAIN, bevel=0.003))
        y += t + 0.012
    # 平放一摞
    n = random.randint(2, 3)
    yy = BY + W_/2 - 0.16
    for k in range(n):
        reg(box(f"flatbook_{i}_{k}", (0.16, 0.2, 0.025),
                (BX-0.01, yy, z+0.03+0.027*k), rot=(0, 0, random.uniform(-0.06, 0.06)), mat=MAT_DEEP))
# 架顶摆件：小盆栽 + 相框
reg(cyl("plant_pot_s", 0.06, 0.1, (BX-0.1, BY+0.5, H_+0.05), mat=MAT_CERAM))
reg(sphere("plant_leaf_s", 0.07, (BX-0.1, BY+0.5, H_+0.16), scale=(1, 1, 1.2), mat=MAT_LEAF))
reg(box("frame_shelf", (0.02, 0.16, 0.22), (BX-0.06, BY-0.45, H_+0.11), rot=(0, D(-8), 0), mat=MAT_DEEP))

# =========================================================
# 9. 落地灯（右后角）
# =========================================================
LX, LY = 2.95, -2.05
reg(cyl("lamp_base", 0.15, 0.025, (LX, LY, 0.0125), mat=MAT_DEEP))
reg(cyl("lamp_pole", 0.014, 1.5, (LX, LY, 0.775)))
reg(cone("lamp_shade", 0.19, 0.13, 0.32, (LX, LY, 1.66), mat=MAT_SOFT))

# =========================================================
# 10. 大绿植（左后角，窗边）
# =========================================================
PX, PY = -2.95, 2.0
reg(cone("plant_pot", 0.20, 0.16, 0.38, (PX, PY, 0.19), mat=MAT_CERAM))
reg(cyl("plant_soil", 0.17, 0.02, (PX, PY, 0.375), mat=MAT_DEEP))
trunks = []
for i in range(3):
    ang = i * D(120)
    trunks.append(cyl(f"trunk_{i}", 0.016, 0.9,
                      (PX+0.05*math.cos(ang), PY+0.05*math.sin(ang), 0.78),
                      rot=(D(8)*math.sin(ang), D(-8)*math.cos(ang), 0), mat=MAT_DEEP))
reg(trunks)
leaves = []
for i in range(9):
    a = random.uniform(0, math.tau)
    r = random.uniform(0.05, 0.3)
    z = random.uniform(1.15, 1.7)
    s = random.uniform(0.10, 0.16)
    leaves.append(sphere(f"leaf_{i}", 1.0, (PX+r*math.cos(a), PY+r*math.sin(a), z),
                         scale=(s, s, s*0.35), mat=MAT_LEAF))
reg(leaves)

# =========================================================
# 11. 吊灯（茶几上方三头）+ 天花筒灯
# =========================================================
CX, CY = 0.1, 1.45
for (dx, dy) in ((0, 0), (-0.16, -0.1), (0.14, -0.12)):
    reg(cyl(f"pend_cord_{dx}_{dy}", 0.004, 0.55, (CX+dx, CY+dy, 2.525)))
    reg(sphere(f"pend_globe_{dx}_{dy}", 0.095, (CX+dx, CY+dy, 2.20), mat=MAT_CERAM))
for i, dx in enumerate((-1.6, -0.5, 0.6, 1.7)):
    reg(cyl("downlight_"+str(i), 0.055, 0.03, (dx, -1.2, 2.785), mat=MAT_DEEP))

# =========================================================
# 12. 墙面画框 ×3
# =========================================================
reg(box("art_back", (0.85, 0.035, 0.6), (1.9, 2.545, 1.7), mat=MAT_DEEP))
reg(box("art_frame_b", (0.95, 0.045, 0.05), (1.9, 2.54, 1.375)))
reg(box("art_frame_t", (0.95, 0.045, 0.05), (1.9, 2.54, 2.025)))
reg(box("art_frame_l", (0.05, 0.045, 0.7), (1.405, 2.54, 1.7)))
reg(box("art_frame_r", (0.05, 0.045, 0.7), (2.395, 2.54, 1.7)))
for i, (y, h) in enumerate(((-1.6, 0.85), (0.4, 0.7))):
    reg(box(f"art_right_{i}", (0.035, 0.62, h), (3.545, y, 1.55), mat=MAT_DEEP))
    reg(box(f"art_right_frame_t_{i}", (0.045, 0.7, 0.045), (3.54, y, 1.55+h/2)))
    reg(box(f"art_right_frame_b_{i}", (0.045, 0.7, 0.045), (3.54, y, 1.55-h/2)))

# =========================================================
# 13. 窗帘（细圆柱褶皱帘 + 帘杆）
# =========================================================
reg(cyl("curtain_rod", 0.016, 3.1, (-3.42, 0, 2.56), rot=(0, D(90), 0)))
for s in (-1.55, 1.55):
    reg(sphere(f"rod_end_{s}", 0.03, (-3.42, s, 2.56)))
n_c = 17
for i in range(n_c):
    y = -1.45 + 2.9 * i / (n_c - 1)
    r = 0.035
    reg(cyl(f"curtain_{i}", r, 1.72, (-3.43 + (0.004 if i % 2 else 0), y, 1.68),
            mat=MAT_SOFT, verts=16))
# 窗边小凳 + 坐垫
reg(box("window_bench", (0.34, 0.9, 0.32), (-3.28, 0.15, 0.16), bevel=0.02))
reg(box("window_bench_cushion", (0.3, 0.84, 0.07), (-3.28, 0.15, 0.355), bevel=0.03, mat=MAT_SOFT))

# =========================================================
# 14. 白模材质统一覆盖（以上各自已带材质，再兜底）
# =========================================================
for o in bpy.data.objects:
    if o.type == 'MESH' and len(o.data.materials) == 0:
        set_mat(o)

# =========================================================
# 15. 灯光：窗光 Sun + 天空 + 室内补光
# =========================================================
def area_light(name, loc, rot, size_x, size_y, energy):
    bpy.ops.object.light_add(type='AREA', location=loc, rotation=rot)
    L = bpy.context.active_object
    L.name = name
    L.data.shape = 'RECTANGLE'
    L.data.size = size_x
    L.data.size_y = size_y
    L.data.energy = energy
    return L

bpy.ops.object.light_add(type='SUN', location=(0, 0, 4))
sun = bpy.context.active_object
sun.data.energy = 3.2
sun.data.angle = D(1.2)
sun.rotation_euler = (D(68), 0, D(-62))   # 低角度从左窗斜射入屋

# 天空环境光（Nishita，关太阳盘，只取天光）
world = bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
wnt = world.node_tree
bg = wnt.nodes["Background"]
sky = wnt.nodes.new("ShaderNodeTexSky")
sky.sky_type = 'SINGLE_SCATTERING'   # Blender 4.x+ 里 Nishita 的新名字
sky.sun_disc = False
sky.sun_elevation = D(22)
sky.sun_rotation = D(-62)
wnt.links.new(sky.outputs[0], bg.inputs[0])
bg.inputs["Strength"].default_value = 0.6

# 室内柔光补光（模拟漫射，撑起白模亮度）
area_light("fill_front", (0, -2.2, 2.1), (D(70), 0, 0), 4.0, 2.0, 110)
area_light("fill_right", (3.2, 0.2, 2.3), (0, D(-75), 0), 1.8, 1.8, 70)
area_light("fill_top",   (0.3, 0.8, 2.72), (0, 0, 0), 2.2, 2.2, 90)

# =========================================================
# 16. 相机 + 多机位渲染
# =========================================================
bpy.ops.object.camera_add()
cam = bpy.context.active_object
cam.data.clip_start = 0.03
scene.camera = cam

SHOTS = [
    # (名字, 相机位置, 注视点, 镜头mm)
    ("A_panorama", (-0.90, -2.35, 1.55), (0.80, 1.40, 0.95), 17),
    ("B_window",   ( 2.70, -2.05, 1.42), (-1.20, 1.60, 0.95), 18),
]

import sys
PREVIEW = "preview" in sys.argv
ONLY = None
for a in sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []:
    if a in ("A", "B"):
        ONLY = a

scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 32 if PREVIEW else 160
scene.cycles.use_denoising = True
scene.cycles.denoiser = 'OPENIMAGEDENOISE'
scene.render.resolution_x = 720 if PREVIEW else 1440
scene.render.resolution_y = 540 if PREVIEW else 1080
scene.view_settings.exposure = -0.2
scene.view_settings.look = 'AgX - Medium High Contrast'

OUT = "/Users/jacksun/Documents/zcode/blender-demo"
for name, loc, tgt, lens in SHOTS:
    if ONLY and not name[0] == ONLY:
        continue
    cam.location = loc
    cam.data.lens = lens
    direction = Vector(tgt) - Vector(loc)
    cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    tag = "preview_" if PREVIEW else ""
    scene.render.filepath = f"{OUT}/{tag}{name}.png"
    print("RENDERING", name, flush=True)
    bpy.ops.render.render(write_still=True)
print("RENDER DONE")

bpy.ops.wm.save_as_mainfile(filepath="/Users/jacksun/Documents/zcode/blender-demo/livingroom.blend")
print("SCENE BUILT, objects:", len(bpy.data.objects))
bpy.ops.render.render(write_still=True)
print("RENDER DONE")
