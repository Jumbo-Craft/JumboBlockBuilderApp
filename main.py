# This is a sample Python script.
import json
import numpy as np

import nbtlib
from nbtlib import Compound, List, String, Int


# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

begin_arr = [
    [0, 0, 15], [15, 15, 15], [0, 15, 0], [0, 15, 0], [15, 15, 0], [0, 15, 15]
]
d_arr = [
    [0, 0, -1], [0, -1, 0], [0, -1, 0], [0, 0, 1], [0, -1, 0], [0, -1, 0]
]
shift_arr = [
    [1, 0, 15], [0, 15, -1], [0, 15, 1], [1, 0, -15], [-1, 15, 0], [1, 15, 0]
]

def main():
    #mk_sample_model()
    #mk_jumbo_model('oak_log',
    #               ['oak_log_top', 'oak_log', 'oak_log', 'oak_log_top', 'oak_log', 'oak_log'],
    #               [0, 1, 2, 3, 4, 5])
    model2nbt('oak_log')

def model2nbt(model_name: str, fill: bool = True):
    nbt = nbtlib.File({
        'size': List[Int]([Int(16), Int(16), Int(16)]),
        'palette': List[Compound]([]),
        'blocks': List[Compound]([]),
        'entities': List[Compound]([]),
        'DataVersion': Int(4671),  # Minecraft 1.21.x
    }, gzipped=True)

    json_model = json.load(open(f'./input/jumbo_models/{model_name}.json','r',encoding='utf-8'))
    blocks = get_block_arr(json_model)

    falling_blocks = json.load(open(f'./input/jumbo_models/{model_name}.json','r',encoding='utf-8'))['values']

    palette_blocks = []
    palette = []
    for i in range(len(blocks)):
        block_name = f'minecraft:{blocks[i]}'
        if block_name in palette_blocks:
            index = palette_blocks.index(block_name)
        else:
            index = len(palette_blocks)
            palette_blocks.append(block_name)
            palette.append(Compound({'Name': String(block_name)}))

        x,y,z = idx2pos(i)
        block = Compound({'pos': List[Int]([Int(x), Int(y), Int(z)]), 'state': Int(index)})
        nbt['blocks'].append(block)

    nbt['palette'] = List[Compound](palette)
    path = f'./output/{model_name}.nbt'
    nbt.save(path)
    print(f'saved: {path}')

def get_block_arr(model: dict):
    faces = model['faces']
    output = ['minecraft:structure_void'] * (16 ** 3)

    for face in faces:
        json_texture = json.load(open(f'./input/jumbo_textures/{face['texture']}.json','r',encoding='utf-8'))

        p = np.array(face['begin'])
        d = np.array(face['direction'])
        slide = np.array(face['shift'])

        for i in range(16**2):
            block = json_texture['components'][i]
            index = pos2idx(tuple(p))
            output[index] = block
            shift = slide if (i + 1) % 16 == 0 else d
            p += shift
    return output

def mk_jumbo_model(model_name: str, textures: list[str], priority: list[int]):
    faces = [{}] * len(textures)
    for i in range(len(textures)):
        p = priority[i]
        faces[p] = {
            'texture': textures[i],
            'begin': begin_arr[i],
            'direction': d_arr[i],
            'shift': shift_arr[i],
        }

    output = {'faces': faces}

    path = f'./output/jumbo_models/{model_name}.json'
    with open(path, mode='w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': '))
        print(f'saved: {path}')

def idx2pos(i: int):
    return i % 16, i // (16**2), (i // 16) % 16

def pos2idx(pos: tuple[int, int, int]):
    return pos[0] + (16**2) * pos[1] + 16 * pos[2]

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()