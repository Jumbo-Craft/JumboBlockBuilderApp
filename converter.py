import json
import numpy as np

import nbtlib
from nbtlib import Compound, List, String, Int


def idx2pos(i: int):
    return i % 16, i // (16 ** 2), (i // 16) % 16


def pos2idx(pos: tuple):
    return pos[0] + (16 ** 2) * pos[1] + 16 * pos[2]


def get_block_arr(model: dict, fill: bool = True):
    faces = model['faces']

    first_texture = json.load(open(f'./input/jumbo_textures/{faces[0]['texture']}.json', 'r', encoding='utf-8'))
    fill_block = f'minecraft:{first_texture['components'][0]}' if fill else 'minecraft:structure_void'
    output = [fill_block] * (16 ** 3)

    falling_blocks = json.load(open(f'./input/falling_block.json', 'r', encoding='utf-8'))['values']

    for face in faces:
        json_texture = json.load(open(f'./input/jumbo_textures/{face['texture']}.json', 'r', encoding='utf-8'))

        p = np.array(face['begin'])
        d = np.array(face['direction'])
        slide = np.array(face['shift'])

        for i in range(16 ** 2):
            block = json_texture['components'][i]
            index = pos2idx(tuple(p))
            output[index] = f'minecraft:{block}'

            if f'minecraft:{block}' in falling_blocks:
                under_pos = p + np.array((0, -1, 0))
                under_index = pos2idx(tuple(under_pos))
                if output[under_index] == 'minecraft:structure_void':
                    output[under_index] = 'minecraft:barrier'

            shift = slide if (i + 1) % 16 == 0 else d
            p += shift
    return output


class Converter:
    __begin_arr = [
        [0, 0, 15], [15, 15, 15], [0, 15, 0], [0, 15, 0], [15, 15, 0], [0, 15, 15]
    ]
    __d_arr = [
        [0, 0, -1], [0, -1, 0], [0, -1, 0], [0, 0, 1], [0, -1, 0], [0, -1, 0]
    ]
    __shift_arr = [
        [1, 0, 15], [0, 15, -1], [0, 15, 1], [1, 0, -15], [-1, 15, 0], [1, 15, 0]
    ]

    def __init__(self, __file_name):
        self.__file_name = __file_name

    def model2nbt(self, fill: bool = True):
        nbt = nbtlib.File({
            'size': List[Int]([Int(16), Int(16), Int(16)]),
            'palette': List[Compound]([]),
            'blocks': List[Compound]([]),
            'entities': List[Compound]([]),
            'DataVersion': Int(4671),  # Minecraft 1.21.x
        }, gzipped=True)

        json_model = json.load(open(f'./input/jumbo_models/{self.__file_name}.json', 'r', encoding='utf-8'))
        blocks = get_block_arr(json_model, fill)

        palette_blocks = []
        palette = []
        for i in range(len(blocks)):
            block_name = blocks[i]
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
        path = f'./output/structure/{self.__file_name}.nbt'
        nbt.save(path)
        print(f'saved: {path}')

    def mk_jumbo_model(self, textures: list[str], priority: list[int]):
        faces = [{}] * len(textures)
        for i in range(len(textures)):
            p = priority[i]
            faces[p] = {
                'texture': textures[i],
                'begin': self.__begin_arr[i],
                'direction': self.__d_arr[i],
                'shift': self.__shift_arr[i],
            }

        output = {'faces': faces}
        path = f'./output/jumbo_models/{self.__file_name}.json'
        with open(path, mode='w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': '))
            print(f'saved: {path}')

