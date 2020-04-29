# -*- coding:utf-8 -*-

import math
import numpy as np
import os

from output.common import level_config
from output.common import level_template
from output.common import level_tile
from output.common import global_params
from SceneSocket.SceneSoketReader import load_scene_sockets_pos_and_chunksize

from images2gif import writeGif

scene_scoket_caches = {}
script_to_template = {}


def gen_script_to_template_map():
    global script_to_template
    for level_info in list(level_config.data.values()):
        level_script = level_info.get('level_script')
        if not level_script:
            continue
        level_template_id = level_info['level_template']
        if level_script in script_to_template:
            if script_to_template[level_script] != level_template_id:
                raise Exception('duplicate level_script %s with different level_template %s, %s' %
                                (level_script, level_template_id, script_to_template[level_script]))
        script_to_template[level_script] = level_template_id


gen_script_to_template_map()

valid_nodes_with_pos = {
    ('50d4b358-eb93-4c49-9422-07bd51e77859', 'Active Reborn Point'): (
        '27507803-6c94-44d6-a92c-7b8829ec0a23', '1a2b0d4d-5987-4dfe-a9d0-1ddcfb5727b4')
    , ('b8bdb1c4-48e3-4c7b-b38e-12aef4a29db0', 'Create Monster'): (
        '33228f1d-1b7a-405d-82d4-7958acc8e8dc', '66e88998-31a7-46fd-9f54-65c5dc2a78e8')
    , ('f7454550-56f5-4242-86a8-9e46b140feab', 'Create Monster Boss'): (
        '8b062406-a831-4a43-baad-9c7bd65a84ef', '4a459fe3-7963-4bcb-acd6-a0372a1ee9a3')
    , ('ae6e4a05-e2e1-4c24-8610-e9a485c1b6ac', 'Create Summon For Player'): (
        '1766bef6-7383-4549-a332-33cc0bc08c64', '133388c9-e68c-46f5-ae60-c17550de17fd')
    , ('83e7076d-9d00-4415-9e9f-d121c6d0d2e6', 'Create NPC'): (
        '7032826b-37c5-4299-a172-2621c92ef289', '9d1e7f79-a2eb-459c-81da-a3014a8924c3')
    , ('8353b9db-48ef-42bb-9d61-5752bb14ce5e', 'Move Unit'): (
        '85705aa7-ecfc-4b37-a95b-423cb42368e8', '3082f47b-5438-4697-be6f-16cd5f57fc91')
    , ('f0f220b5-e584-4aff-8c86-f039d030c02b', 'Create Mechanism'): (
        'b84f6f5c-695f-4b56-b98b-3bd61698bd3c', 'bb186896-158c-4956-9962-692ad0d4193f')
    , ('32439db5-f1b3-4c5f-b0cd-513a4facb4c7', 'Create Occupation'): (
        '158a9319-06fb-43a2-b5e1-77cf35b887da', '5bd06870-6e3a-4ab2-bfb0-69952a802f29')
    , ('03cfda15-a336-4c6c-b8a4-75123e88628d', 'Create Mechanism With Lightmap'): (
        '6ba0ed20-2902-4c68-a618-4eed19e5af3a', '19a0fb50-6797-4034-b00c-d7c3a101f1dd')
    , ('236ec09a-fe30-45eb-ad16-eb47429b334e', 'Transport Unit To'): (
        'b7ae3ff7-373d-4efc-8678-74d63edfb2f9', '4cb06366-5950-4971-9358-18133a94630d')
}


def is_node_with_pos(node):
    return (node.nodeType, node.name) in valid_nodes_with_pos


def get_scene_socket(scene_path, markerPoint, resPath):
    """
    scene_socket的解析脚本在本脚本导出之后,所以不能直接用scene_scoket.py
    """
    if scene_path not in scene_scoket_caches:
        fullname = os.path.join(resPath, scene_path)
        socketspos, chunk_size = load_scene_sockets_pos_and_chunksize(resPath, fullname)
        scene_scoket_caches[scene_path] = socketspos

    return scene_scoket_caches[scene_path].get(markerPoint)


def get_pos_from_template(levelTemplate, markerPoint, tileIndex, resPath):
    tiles = level_template.data[levelTemplate]['tiles']

    if not tileIndex:
        for tileInfo in tiles:
            tilename = tileInfo['tile_name']
            scene_path = level_tile.data[tilename]['model_path']
            pointInfo = get_scene_socket(scene_path, markerPoint, resPath)
            if pointInfo:
                pos_list = list(map(float, pointInfo['pos'].split(',')))
                return pos_list[0] + tileInfo['x'], pos_list[1] + tileInfo['y'], pos_list[2] + tileInfo['z']
    else:
        for tileInfo in tiles:
            if tileIndex == tileInfo['tile_index']:
                tilename = tileInfo['tile_name']
                scene_path = level_tile.data[tilename]['model_path']
                pointInfo = get_scene_socket(scene_path, markerPoint, resPath)
                if pointInfo:
                    pos_list = list(map(float, pointInfo['pos'].split(',')))
                    return pos_list[0] + tileInfo['x'], pos_list[1] + tileInfo['y'], pos_list[2] + tileInfo['z']

    raise Exception('_parse_tile_scene_path error no markerPoint levelTemplate %s, markerPoint %s, tileIndex %s' % (
        levelTemplate, markerPoint, tileIndex))


def get_node_pos(node, levelScript, resPath):
    posItems = valid_nodes_with_pos.get((node.nodeType, node.name))
    if not posItems:
        return None
    markerPointId, tileIndexId = posItems
    d1 = node.args[markerPointId].get('dataProvider')
    d2 = node.args[tileIndexId].get('dataProvider')
    if (d1 and d1 is not node) or (d2 and d2 is not node):
        # 连线的pos不参与位置信息生成
        return None
    markerPoint = node.args[markerPointId]['valueRef'].value
    tileIndex = node.args[tileIndexId]['valueRef'].value
    if not markerPoint:
        raise Exception(
            'node after first time nearby does not support link type or None value level = %s, node.name = %s' % (
                levelScript, node.name))
    levelTemplate = script_to_template[levelScript]
    return get_pos_from_template(levelTemplate, markerPoint, tileIndex, resPath)


def recursion_linked_pos_node(nodeGraph, node, levelScript, visited_nodes, trigger_poses, resPath):
    if node in visited_nodes:
        return
    visited_nodes.add(node)
    if is_node_with_pos(node):
        pos = get_node_pos(node, levelScript, resPath)
        if pos:
            trigger_poses.append(pos)
        return
    for linkinfo in list(node.eventLinks.values()):
        for link in linkinfo['links']:
            endNode = link['node']
            recursion_linked_pos_node(nodeGraph, endNode, levelScript, visited_nodes, trigger_poses, resPath)


def parse_linked_pos_node(nodeGraph, node, levelScript, resPath):
    if levelScript not in script_to_template:
        print(('check script ', levelScript, ' whether unused anymore'))
        return None

    visited_nodes = set()
    trigger_poses = []
    recursion_linked_pos_node(nodeGraph, node, levelScript, visited_nodes, trigger_poses, resPath)
    trigger_poses = set((pos[0], (pos[2])) for pos in trigger_poses)
    trigger_grids = set()
    for pos in trigger_poses:
        trigger_grids.update(extend_grids(pos, levelScript))

    trigger_grids_list = []

    for grid in trigger_grids:
        trigger_grids_list.append(grid[0])
        trigger_grids_list.append(grid[1])
    return tuple(trigger_grids_list)


def check_and_add_offset(pos, grid_x, grid_y, grid_offset_x, grid_offset_y, pos_offset_x, pos_offset_y, aoi_grid_size,
                         make_up_offsets, max_x, max_y):
    pos_offset_x_l = (grid_x + grid_offset_x) * aoi_grid_size + pos_offset_x
    pos_offset_x_r = pos_offset_x_l + aoi_grid_size
    pos_offset_y_b = (grid_y + grid_offset_y) * aoi_grid_size + pos_offset_y
    pos_offset_y_t = pos_offset_y_b + aoi_grid_size
    distance_x = pos_offset_x_l - pos[0] if pos[0] <= pos_offset_x_l else (
        0 if pos[0] <= pos_offset_x_r else pos[0] - pos_offset_x_r)
    distance_y = pos_offset_y_b - pos[1] if pos[1] <= pos_offset_y_b else (
        0 if pos[1] <= pos_offset_y_t else pos[1] - pos_offset_y_t)
    if math.sqrt(distance_x * distance_x + distance_y * distance_y) < 200:
        make_up_offsets.add((max(0, min(grid_x + grid_offset_x, max_x)), max(0, min(grid_y + grid_offset_y, max_y))))
        return True
    return False


def extend_grids(pos, levelScript):
    aoi_grid_size = global_params.data['aoi_grid_size']['value']
    levelTemplate = script_to_template[levelScript]
    level_info = level_template.data[levelTemplate]
    pos_offset_x = int(level_info['minx'])
    pos_offset_y = int(level_info['miny'])

    grid_x = int((pos[0] - pos_offset_x) / aoi_grid_size)
    grid_y = int((pos[1] - pos_offset_y) / aoi_grid_size)

    max_x = (int(level_info['maxx'] - level_info['minx']) - 1) / aoi_grid_size
    max_y = (int(level_info['maxy'] - level_info['miny']) - 1) / aoi_grid_size
    make_up_offsets = set()
    grid_offset_x = 0
    while True:
        grid_offset_y = 0
        while True:
            hit = False
            hit |= check_and_add_offset(pos, grid_x, grid_y, grid_offset_x, grid_offset_y, pos_offset_x, pos_offset_y,
                                        aoi_grid_size, make_up_offsets, max_x, max_y)
            hit |= check_and_add_offset(pos, grid_x, grid_y, grid_offset_x, -grid_offset_y, pos_offset_x, pos_offset_y,
                                        aoi_grid_size, make_up_offsets, max_x, max_y)
            hit |= check_and_add_offset(pos, grid_x, grid_y, -grid_offset_x, grid_offset_y, pos_offset_x, pos_offset_y,
                                        aoi_grid_size, make_up_offsets, max_x, max_y)
            hit |= check_and_add_offset(pos, grid_x, grid_y, -grid_offset_x, -grid_offset_y, pos_offset_x, pos_offset_y,
                                        aoi_grid_size, make_up_offsets, max_x, max_y)
            if not hit:
                break
            grid_offset_y += 1
        if grid_offset_y == 0:
            break
        grid_offset_x += 1

    return make_up_offsets


colors = ((255, 0, 0), (255, 255, 0), (128, 255, 0), (255, 0, 255),
          (0, 128, 255), (128, 0, 255), (0, 255, 255), (0, 255, 0),
          (255, 128, 0), (255, 0, 128), (0, 255, 128), (0, 0, 255),
          (0, 0, 128), (0, 128, 0), (0, 128, 128), (128, 0, 0),
          (128, 0, 128), (128, 128, 0), (128, 128, 255), (128, 255, 128))


def gen_preview_pic(trigger_grids_list, outputPath, levelScript):
    if not trigger_grids_list:
        return
    try:
        import png
    except ImportError:
        return

    scale = 4

    aoi_grid_size = global_params.data['aoi_grid_size']['value'] / scale
    levelTemplate = script_to_template[levelScript]
    level_info = level_template.data[levelTemplate]
    x_size = int(level_info['maxx'] - level_info['minx']) / scale
    y_size = int(level_info['maxy'] - level_info['miny']) / scale

    pixels = [[255, 255, 255] * x_size for t in range(y_size)]
    grids_writed = set()
    color_index = 0
    image_list = []

    tmp_pixels = [[[255, 255, 255] for k in range(x_size)] for t in range(y_size)]
    for _, grids in list(trigger_grids_list.values()):
        color = colors[color_index % len(colors)]
        color_index += 1
        for index in range(0, len(grids), 2):
            x = grids[index]
            y = grids[index + 1]
            if (x, y) in grids_writed:
                r = channel_blend_average(pixels[y_size - 1 - y * aoi_grid_size][3 * x * aoi_grid_size], color[0])
                g = channel_blend_average(pixels[y_size - 1 - y * aoi_grid_size][3 * x * aoi_grid_size + 1], color[1])
                b = channel_blend_average(pixels[y_size - 1 - y * aoi_grid_size][3 * x * aoi_grid_size + 2], color[2])
            else:
                grids_writed.add((x, y))
                r, g, b = color
            for i in range(x * aoi_grid_size, x * aoi_grid_size + aoi_grid_size):
                for j in range(y_size - 1 - y * aoi_grid_size, y_size - 1 - y * aoi_grid_size - aoi_grid_size, -1):
                    if 0 <= j < y_size and 0 <= i < x_size:
                        pixels[j][3 * i] = r
                        pixels[j][3 * i + 1] = g
                        pixels[j][3 * i + 2] = b

                        tmp_pixels[j][i][0] = color[0]
                        tmp_pixels[j][i][1] = color[1]
                        tmp_pixels[j][i][2] = color[2]

        image_list.append(np.array(tmp_pixels))

    writeGif(outputPath.split('.png')[0] + '.gif', image_list, duration=0.3, nq=0, subRectangles=False)

    f = open(outputPath, 'wb')
    w = png.Writer(x_size, y_size)
    w.write(f, pixels)
    f.close()


def channel_blend_normal(c1, c2):
    return c1


def channel_blend_lighten(c1, c2):
    return c2 if c2 > c1 else c1


def channel_blend_darken(c1, c2):
    return c1 if c2 > c1 else c2


def channel_blend_multiply(c1, c2):
    return c1 * c2 / 255


def channel_blend_average(c1, c2):
    return (c1 + c2) / 2


def channel_blend_add(c1, c2):
    return min(255, c1 + c2)


def channel_blend_subtract(c1, c2):
    return 0 if c1 + c2 < 255 else c1 + c2 - 255


def channel_blend_difference(c1, c2):
    return abs(c1 - c2)


def channel_blend_negation(c1, c2):
    return 255 - abs(255 - c1 - c2)


def channel_blend_screen(c1, c2):
    return 255 - (((255 - c1) * (255 - c2)) >> 8)


def channel_blend_exclusion(c1, c2):
    return c1 + c2 - 2 * c1 * c2 / 255


def channel_blend_overlay(c1, c2):
    return 2 * c1 * c2 / 255 if c2 < 128 else 255 - 2 * (255 - c1) * (255 - c2) / 255


def channel_blend_softlight(c1, c2):
    return 2 * ((c1 >> 1) + 64) * c2 / 255 if c2 < 128 else 255 - 2 * (255 - ((c1 >> 1) + 64)) * (255 - c2) / 255


def channel_blend_hardlight(c1, c2):
    return 2 * c1 * c2 / 255 if c1 < 128 else 255 - 2 * (255 - c1) * (255 - c2) / 255


def channel_blend_colordodge(c1, c2):
    return 255 if c2 == 255 else min(255, (c1 << 8) / (255 - c2))


def channel_blend_colorburn(c1, c2):
    return 0 if c2 == 0 else max(0, 255 - ((255 - c1) << 8) / c2)


def channel_blend_lineardodge(c1, c2):
    return min(255, c1 + c2)


def channel_blend_linearburn(c1, c2):
    return 0 if c1 + c2 < 255 else c1 + c2 - 255


def channel_blend_linearlight(c1, c2):
    return 0 if c1 + 2 * c2 < 255 else c1 + 2 * c2 - 255 if c2 < 128 else min(c1, 2 * (c2 - 128))


def channel_blend_vividlight(c1, c2):
    return 0 if c2 == 0 else max(0, 255 - ((255 - c1) << 8) / (2 * c2)) if c2 < 128 else 255 if 2 * (
            c2 - 128) == 255 else min(255, (c1 << 8) / (255 - 2 * (c2 - 128)))


def channel_blend_pinlight(c1, c2):
    return c1 if 2 * c2 > c1 else 2 * c2 if c2 < 128 else 2 * (c2 - 128) if 2 * (c2 - 128) > c1 else c1


def channel_blend_hardmix(c1, c2):
    return 0 if channel_blend_vividlight(c1, c2) < 128 else 255


def channel_blend_reflect(c1, c2):
    return 255 if c2 == 255 else min(255, c1 * c1 / (255 - c2))


def channel_blend_glow(c1, c2):
    return 255 if c1 == 255 else min(255, c2 * c2 / (255 - c1))


def channel_blend_phoenix(c1, c2):
    return min(c1, c2) - max(c1, c2) + 255


all = [channel_blend_normal, channel_blend_lighten, channel_blend_darken, channel_blend_multiply,
       channel_blend_average, channel_blend_add, channel_blend_subtract, channel_blend_difference,
       channel_blend_negation, channel_blend_screen, channel_blend_exclusion, channel_blend_overlay,
       channel_blend_softlight, channel_blend_hardlight, channel_blend_colordodge, channel_blend_colorburn,
       channel_blend_lineardodge, channel_blend_linearburn, channel_blend_linearlight, channel_blend_vividlight,
       channel_blend_pinlight, channel_blend_hardmix, channel_blend_reflect, channel_blend_glow, channel_blend_phoenix]

if __name__ == '__main__':
    for f in all:
        print((f.__name__, f(0, 0)))
