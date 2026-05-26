import json
from pathlib import Path

import nbtlib
import numpy as np
from nbtlib import Compound, List, String, Int


def idx2pos(i: int):
    return i % 16, i // (16 ** 2), (i // 16) % 16


def pos2idx(pos: tuple):
    return pos[0] + (16 ** 2) * pos[1] + 16 * pos[2]


def get_block_arr(model: dict):
    faces = model['faces']
    is_empty = model['is_empty']

    first_texture = json.load(open(faces[0]['texture'], 'r', encoding='utf-8'))
    inside_block = 'minecraft:structure_void' if is_empty else f'minecraft:{first_texture['components'][0]}'
    output = [inside_block] * (16 ** 3)

    falling_blocks = json.load(open(f'./input/falling_block.json', 'r', encoding='utf-8'))['values']
    vec = {
        'B': {'begin': [0, 0, 15], 'shift': [0, 0, -1], 'slide': [1, 0, 15]},
        'E': {'begin': [15, 15, 15], 'shift': [0, -1, 0], 'slide': [0, 15, -1]},
        'W': {'begin': [0, 15, 0], 'shift': [0, -1, 0], 'slide': [0, 15, 1]},
        'T': {'begin': [0, 15, 0], 'shift' : [0, 0, 1], 'slide': [1, 0, -15]},
        'N': {'begin': [15, 15, 0], 'shift': [0, -1, 0], 'slide': [-1, 15, 0]},
        'S': {'begin': [0, 15, 15], 'shift': [0, -1, 0], 'slide': [1, 15, 0]},
    }

    for face in faces:
        json_texture = json.load(open(face['texture'], 'r', encoding='utf-8'))
        d = face['direction']
        p = np.array(vec[d]['begin'])
        shift = np.array(vec[d]['shift'])
        slide = np.array(vec[d]['slide'])

        for i in range(16 ** 2):
            block = json_texture['components'][i]
            index = pos2idx(tuple(p))
            output[index] = f'minecraft:{block}'

            if f'minecraft:{block}' in falling_blocks:
                under_pos = p + np.array((0, -1, 0))
                under_index = pos2idx(tuple(under_pos))
                if output[under_index] == 'minecraft:structure_void':
                    output[under_index] = 'minecraft:barrier'

            p += slide if (i + 1) % 16 == 0 else shift
    return output


def model2nbt(model_path: str):
    p = Path(model_path)
    file_name = p.stem

    nbt = nbtlib.File({
        'size': List[Int]([Int(16), Int(16), Int(16)]),
        'palette': List[Compound]([]),
        'blocks': List[Compound]([]),
        'entities': List[Compound]([]),
        'DataVersion': Int(4671),  # Minecraft 1.21.x
    }, gzipped=True)

    json_model = json.load(open(model_path, 'r', encoding='utf-8'))
    blocks = get_block_arr(json_model)

    palette_blocks = []
    palette = []
    for i in range(len(blocks)):
        block_name = blocks[i]

        if block_name == 'minecraft:structure_void':
            continue

        if block_name in palette_blocks:
            index = palette_blocks.index(block_name)
        else:
            index = len(palette_blocks)
            palette_blocks.append(block_name)
            palette.append(Compound({'Name': String(block_name)}))

        x, y, z = idx2pos(i)
        block = Compound({'pos': List[Int]([Int(x), Int(y), Int(z)]), 'state': Int(index)})
        nbt['blocks'].append(block)

    nbt['palette'] = List[Compound](palette)
    path = f'{p.parent}\\{file_name}.nbt'
    nbt.save(path)
    print(f'saved: {path}')


def mk_jumbo_model(faces: list[dict], path: str, is_empty):
    output = {
        'faces': faces,
        'is_empty': is_empty
    }
    with open(path, mode='w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': '))
        print(f'saved: {path}')

