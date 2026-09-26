import bpy, math

# 清空默认场景
bpy.ops.wm.read_factory_settings(use_empty=True)

# 主体：经典猴头 Suzanne
bpy.ops.mesh.primitive_monkey_add(location=(0, 0, 1))
monkey = bpy.context.active_object
mat = bpy.data.materials.new("Orange")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.8, 0.35, 0.05, 1)
bsdf.inputs["Roughness"].default_value = 0.3
monkey.data.materials.append(mat)

# 地面
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))

# 灯光 + 相机
bpy.ops.object.light_add(type='SUN', location=(4, -4, 6))
bpy.context.active_object.data.energy = 4
bpy.ops.object.light_add(type='AREA', location=(-3, -3, 3))
lamp = bpy.context.active_object
lamp.data.energy = 300
lamp.rotation_euler = (math.radians(55), 0, math.radians(-45))
bpy.ops.object.camera_add(location=(5.2, -5.2, 3.4), rotation=(math.radians(65), 0, math.radians(45)))
bpy.context.scene.camera = bpy.context.active_object

# 渲染设置：Cycles CPU，小图快速出图
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 32
scene.cycles.device = 'CPU'
scene.render.resolution_x = 480
scene.render.resolution_y = 480
scene.render.filepath = "/Users/jacksun/Documents/zcode/blender-demo/render.png"
bpy.ops.render.render(write_still=True)

# 另存 .blend 工程文件
bpy.ops.wm.save_as_mainfile(filepath="/Users/jacksun/Documents/zcode/blender-demo/demo.blend")
print("DEMO OK")
