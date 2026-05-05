import json
import os
import re
import sys
from copy import copy

root = os.path.dirname(__file__)
dictionary_file = os.path.join(root, 'vendor/animCJK/dictionaryJa.txt')
graphics_file = os.path.join(root, 'vendor/animCJK/graphicsJa.txt')
graphics_kana_file = os.path.join(root, 'vendor/animCJK/graphicsJaKana.txt')
graphics_number_file = os.path.join(root, 'vendor/animNumber/graphicsNumber.txt')
output_dir = os.path.join(root, 'data')

# animNumber digits are placed at Klee One's native size with baseline at
# animNumber source y=28, so the only transform applied here is a Y translation
# that maps the digit's natural bottom (y=12 in animNumber data) to animCJK's
# typical character bottom (y≈1). X is anchored around the canvas x-center.
NUMBER_SCALE = 1.0
NUMBER_ORIGIN_X = 512
NUMBER_BOTTOM_SOURCE = 12
NUMBER_BOTTOM_TARGET = 1

PATH_CMD_SPLIT_RE = re.compile(r'([MLCQZ])')
PATH_NUM_RE = re.compile(r'-?\d+(?:\.\d+)?')


def scale_point(x, y):
    nx = (x - NUMBER_ORIGIN_X) * NUMBER_SCALE + NUMBER_ORIGIN_X
    ny = (y - NUMBER_BOTTOM_SOURCE) * NUMBER_SCALE + NUMBER_BOTTOM_TARGET
    return round(nx), round(ny)


def scale_path(path):
    out = []
    for piece in PATH_CMD_SPLIT_RE.split(path):
        if piece in ('M', 'L', 'C', 'Q', 'Z'):
            out.append(piece)
            continue
        nums = PATH_NUM_RE.findall(piece)
        pairs = []
        for i in range(0, len(nums) - 1, 2):
            nx, ny = scale_point(float(nums[i]), float(nums[i + 1]))
            pairs.append(f'{nx} {ny}')
        out.append(' '.join(pairs))
    return ''.join(out)


def scale_animnumber_entry(entry):
    entry['strokes'] = [scale_path(s) for s in entry['strokes']]
    entry['medians'] = [
        [list(scale_point(p[0], p[1])) for p in stroke]
        for stroke in entry['medians']
    ]
    return entry

positioners = {
    '⿰': 2,
    '⿱': 2,
    '⿲': 3,
    '⿳': 3,
    '⿴': 2,
    '⿵': 2,
    '⿶': 2,
    '⿷': 2,
    '⿸': 2,
    '⿹': 2,
    '⿺': 2,
    '⿻': 2,
}
missing_marker = '？'

graphics_data = {}
dict_data = {}

with open(dictionary_file) as f:
    lines = f.readlines()
    for line in lines:
        decoded_line = json.loads(line)
        dict_data[decoded_line['character']] = decoded_line

for gfx_file in [graphics_file, graphics_kana_file, graphics_number_file]:
    is_number_file = (gfx_file == graphics_number_file)
    with open(gfx_file) as f:
        lines = f.readlines()
        for line in lines:
            # Fixing a weird issue with the JSON in 抽
            decoded_line = json.loads(line.replace('[C,', '['))
            char = decoded_line.pop('character')
            # On macOS, skip CJK Compatibility Ideographs (U+F900-U+FAFF)
            # because APFS normalizes filenames via NFC, causing these to
            # overwrite the standard CJK Unified Ideograph files.
            if sys.platform == 'darwin' and len(char) == 1 and 0xF900 <= ord(char) <= 0xFAFF:
                continue
            if is_number_file:
                decoded_line = scale_animnumber_entry(decoded_line)
            graphics_data[char] = decoded_line


def get_decomp_index(char, subchar):
    "Parse the decomposition tree to figure out what the index of the subchar is within the char"
    stack = []
    for piece in dict_data[char]['decomposition']:
        last_node = None
        path = []
        if len(stack) > 0:
            last_node = stack.pop()
            path = copy(last_node['path'])
            path.append(last_node['children'])
            last_node['children'] += 1
            if last_node['children'] < last_node['size']:
                stack.append(last_node)
        if piece in positioners:
            node = {
                'size': positioners[piece],
                'children': 0,
                'path': path,
            }
            stack.append(node)
        elif piece == subchar:
            return path
    return None


def get_radical_strokes(char):
    return None
    # TODO: figure out how to derive radical in animCJK format
    radical = dict_data[char]['radical']
    if char == radical:
        return None
    decomp_index = get_decomp_index(char, radical)
    if not decomp_index:
        return None
    rad_strokes = []
    for stroke_num, match_index in enumerate(dict_data[char]['matches']):
        if match_index == decomp_index:
            rad_strokes.append(stroke_num)
    return rad_strokes


# write out data

for char in graphics_data:
    radical = get_radical_strokes(char)
    if radical:
        graphics_data[char]['radStrokes'] = radical

for char, data in graphics_data.items():
    out_file = os.path.join(output_dir, f'{char}.json')
    with open(out_file, 'w') as f:
        f.write(json.dumps(data, ensure_ascii=False))

with open(os.path.join(output_dir, 'all.json'), 'w') as f:
    f.write(json.dumps(graphics_data, ensure_ascii=False))
