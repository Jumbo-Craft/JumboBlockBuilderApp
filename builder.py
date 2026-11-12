import json
from pathlib import Path

import nbtlib
import numpy as np
from nbtlib import Compound, List, String, Int


def idx2pos(i: int):
    return i % 16, i // (16 ** 2), (i // 16) % 16


def pos2idx(pos: tuple):
    return pos[0] + (16 ** 2) * pos[1] + 16 * pos[2]


falling_blocks = json.load(open(f'./input/falling_block.json', 'r', encoding='utf-8'))['values']
stained_glasses = json.load(open(f'./input/stained_glass.json', 'r', encoding='utf-8'))['values']

cube_vec = {
    'B': {'begin': [0, 0, 15], 'shift': [0, 0, -1], 'slide': [1, 0, 15]},
    'E': {'begin': [15, 15, 15], 'shift': [0, -1, 0], 'slide': [0, 15, -1]},
    'W': {'begin': [0, 15, 0], 'shift': [0, -1, 0], 'slide': [0, 15, 1]},
    'T': {'begin': [0, 15, 0], 'shift': [0, 0, 1], 'slide': [1, 0, -15]},
    'N': {'begin': [15, 15, 0], 'shift': [0, -1, 0], 'slide': [-1, 15, 0]},
    'S': {'begin': [0, 15, 15], 'shift': [0, -1, 0], 'slide': [1, 15, 0]}
}

cross_vec = {
    'cross1': {'begin': [0, 15, 0], 'shift': [0, -1, 0], 'slide': [1, 15, 1]},
    'cross2': {'begin': [15, 15, 0], 'shift': [0, -1, 0], 'slide': [-1, 15, 1]}
}


def get_block_arr(faces: list[tuple[str, str]], inside: str, vec: dict):
    output = [inside] * (16 ** 3)

    for face in faces:
        json_texture = json.load(open(face[1], 'r', encoding='utf-8'))
        d = face[0]
        p = np.array(vec[d]['begin'])
        shift = np.array(vec[d]['shift'])
        slide = np.array(vec[d]['slide'])

        for i in range(16 ** 2):
            block = f'minecraft:{json_texture['components'][i]}'
            index = pos2idx(tuple(p))
            output[index] = block

            if block in falling_blocks:
                under_pos = p + np.array((0, -1, 0))
                under_index = pos2idx(tuple(under_pos))
                if output[under_index] == 'minecraft:structure_void':
                    output[under_index] = 'minecraft:barrier'

            if block == 'minecraft:structure_void':
                over_pos = p + np.array((0, 1, 0))
                over_index = pos2idx(tuple(over_pos))
                if 0 <= over_index < len(output) and output[over_index] in falling_blocks:
                    output[index] = 'minecraft:barrier'

            p += slide if (i + 1) % 16 == 0 else shift

    return output


def model2nbt(src: Path, dst: Path):
    json_model = json.load(open(src, 'r', encoding='utf-8'))
    parent = json_model.get('parent')
    name = src.stem

    if f'minecraft:{name}' in stained_glasses:
        print(f'skipped (unsupported block: {name}): {src}')
        return

    if parent == 'minecraft:block/cube':
        blocks = cube(name, json_model)
    elif parent == 'minecraft:block/cube_all':
        blocks = cube_all(name, json_model)
    elif parent == 'minecraft:block/cube_column':
        blocks = cube_column(name, json_model)
    elif parent == 'minecraft:block/cube_bottom_top':
        blocks = cube_bottom_top(name, json_model)
    elif parent == 'minecraft:block/cube_top':
        blocks = cube_top(name, json_model)
    elif parent == 'minecraft:block/cube_directional':
        blocks = cube_directional(name, json_model)
    elif parent == 'minecraft:block/orientable':
        blocks = orientable(name, json_model)
    elif parent == 'minecraft:block/orientable_with_bottom':
        blocks = orientable_with_bottom(name, json_model)
    else:
        print(f'skipped (unsupported parent: {parent}): {src}')
        return

    nbt = nbtlib.File({
        'size': List[Int]([Int(16), Int(16), Int(16)]),
        'palette': List[Compound]([]),
        'blocks': List[Compound]([]),
        'entities': List[Compound]([]),
        'DataVersion': Int(4671),  # Minecraft 1.21.x
    }, gzipped=True)

    palette_blocks = []
    palette = []
    for i, block_name in enumerate(blocks):
        if block_name == 'minecraft:structure_void':
            continue

        if block_name in palette_blocks:
            index = palette_blocks.index(block_name)
        else:
            index = len(palette_blocks)
            palette_blocks.append(block_name)
            palette.append(Compound({'Name': String(block_name)}))

        x, y, z = idx2pos(i)
        nbt['blocks'].append(
            Compound({'pos': List[Int]([Int(x), Int(y), Int(z)]), 'state': Int(index)})
        )

    nbt['palette'] = List[Compound](palette)

    dst.parent.mkdir(parents=True, exist_ok=True)
    nbt.save(dst)
    print(f'saved: {dst}')


def convert_all(src_root: str = 'input/models/block', dst_root: str = 'output/structure'):
    src_root = Path(src_root)
    dst_root = Path(dst_root)

    if not src_root.exists():
        print(f'not found: {src_root.resolve()}')
        return

    files = sorted(src_root.rglob('*.json'))
    print(f'found {len(files)} files in {src_root.resolve()}')

    for src in files:
        dst = (dst_root / src.relative_to(src_root)).with_suffix('.nbt')
        #print(dst)
        model2nbt(src, dst)


def mk_jumbo_model(model_type: str, faces: list[dict], path: str, inside: str):
    output = {
        'model_type': model_type,
        'faces': faces,
        'inside': inside
    }
    with open(path, mode='w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': '))
        print(f'saved: {path}')


def cube(name: str, model: dict):
    textures = model['textures']
    down = textures['down'].split('/')[1]
    up = textures['up'].split('/')[1]
    east = textures['east'].split('/')[1]
    west = textures['west'].split('/')[1]
    north = textures['north'].split('/')[1]
    south = textures['south'].split('/')[1]

    faces = [
        ('B', f'./input/jumbo_textures/{down}.json'),
        ('E', f'./input/jumbo_textures/{east}.json'),
        ('W', f'./input/jumbo_textures/{west}.json'),
        ('T', f'./input/jumbo_textures/{up}.json'),
        ('N', f'./input/jumbo_textures/{north}.json'),
        ('S', f'./input/jumbo_textures/{south}.json')
    ]

    return get_block_arr(faces, f'minecraft:{name}', cube_vec)


def cube_all(name: str, model: dict):
    textures = model['textures']
    tx = textures['all'].split('/')[1]

    faces = [
        (d, f'./input/jumbo_textures/{tx}.json') for d in ['B', 'E', 'W', 'T', 'N', 'S']
    ]

    return get_block_arr(faces, f'minecraft:{name}', cube_vec)


def cube_column(name: str, model: dict):
    textures = model['textures']
    end = textures['end'].split('/')[1]
    side = textures['side'].split('/')[1]

    faces = [
        ('B', f'./input/jumbo_textures/{end}.json'),
        ('E', f'./input/jumbo_textures/{side}.json'),
        ('W', f'./input/jumbo_textures/{side}.json'),
        ('T', f'./input/jumbo_textures/{end}.json'),
        ('N', f'./input/jumbo_textures/{side}.json'),
        ('S', f'./input/jumbo_textures/{side}.json')
    ]

    return get_block_arr(faces, f'minecraft:{name}', cube_vec)


def cube_bottom_top(name: str, model: dict):
    textures = model['textures']
    bottom = textures['bottom'].split('/')[1]
    side = textures['side'].split('/')[1]
    top = textures['top'].split('/')[1]

    faces = [
        ('B', f'./input/jumbo_textures/{bottom}.json'),
        ('E', f'./input/jumbo_textures/{side}.json'),
        ('W', f'./input/jumbo_textures/{side}.json'),
        ('T', f'./input/jumbo_textures/{top}.json'),
        ('N', f'./input/jumbo_textures/{side}.json'),
        ('S', f'./input/jumbo_textures/{side}.json')
    ]

    return get_block_arr(faces, f'minecraft:{name}', cube_vec)


def cube_top(name: str, model: dict):
    textures = model['textures']
    side = textures['side'].split('/')[1]
    top = textures['top'].split('/')[1]

    faces = [
        ('B', f'./input/jumbo_textures/{side}.json'),
        ('E', f'./input/jumbo_textures/{side}.json'),
        ('W', f'./input/jumbo_textures/{side}.json'),
        ('T', f'./input/jumbo_textures/{top}.json'),
        ('N', f'./input/jumbo_textures/{side}.json'),
        ('S', f'./input/jumbo_textures/{side}.json')
    ]

    return get_block_arr(faces, f'minecraft:{name}', cube_vec)

def cube_directional(name: str, model: dict):
    return cube(name, model)

def orientable(name: str, model: dict):
    textures = model['textures']
    top = textures['top'].split('/')[1]
    front = textures['front'].split('/')[1]
    side = textures['side'].split('/')[1]

    faces = [
        ('B', f'./input/jumbo_textures/{top}.json'),
        ('E', f'./input/jumbo_textures/{side}.json'),
        ('W', f'./input/jumbo_textures/{side}.json'),
        ('T', f'./input/jumbo_textures/{top}.json'),
        ('N', f'./input/jumbo_textures/{front}.json'),
        ('S', f'./input/jumbo_textures/{side}.json')
    ]

    return get_block_arr(faces, f'minecraft:{name}', cube_vec)


def orientable_with_bottom(name: str, model: dict):
    textures = model['textures']
    top = textures['top'].split('/')[1]
    front = textures['front'].split('/')[1]
    side = textures['side'].split('/')[1]
    bottom = textures['bottom'].split('/')[1]

    faces = [
        ('B', f'./input/jumbo_textures/{bottom}.json'),
        ('E', f'./input/jumbo_textures/{side}.json'),
        ('W', f'./input/jumbo_textures/{side}.json'),
        ('T', f'./input/jumbo_textures/{top}.json'),
        ('N', f'./input/jumbo_textures/{front}.json'),
        ('S', f'./input/jumbo_textures/{side}.json')
    ]

    return get_block_arr(faces, f'minecraft:{name}', cube_vec)