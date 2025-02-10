import json
import math
import base64
import numpy as np
from PIL import Image

def fread(path):
    data = None
    with open(path, "r") as file:
        data = file.read()
    return data

def freadbytes(path):
    data = None
    with open(path, "rb") as file:
        data = file.read()
    return data

def fwrite(data, path):
    with open(path, "w") as file:
        file.write(data)

def fwritebytes(data, path):
    with open(path, "wb") as file:
        file.write(data)

def iread(path):
    image = Image.open(path)
    pixel_data = list(image.getdata())
    return pixel_data

def iwrite(data, path):
    image = Image.fromarray(data)
    image.save(path)

def bitmapListTo2DArray(data, row_size):
    result = []
    row = []
    column_counter = 0
    for pixel in data:
        row.append(pixel)
        column_counter += 1
        if column_counter == row_size:
            result.append(row)
            column_counter = 0
            row = []
    return result

def jdump(data):
    return json.dumps(data)

def jparse(data):
    clean_data = data.replace("\x00", "")
    parsed_data = {}
    try:
        parsed_data = json.loads(clean_data)
    except:
        print("could not read decrypted data")
    return parsed_data

def bencode(data):
    return "".join("{0:08b}".format(ord(x)) for x in data)

def bdecode(data):
    raw_data = data
    index = 0
    result = ""
    while len(raw_data) > 0:
        if len(raw_data) > 0:
            result += chr(int(raw_data[:8], 2))
            raw_data = raw_data[8:]
        else:
            break
    return result

def loadCyphermap(path, key):
    hashword = minihash(key)
    decrypted_data = jparse(destepcrypt(bdecode(readCyphermap(path)), hashword))
    return decrypted_data

def minihash(data):
    sd = data[:32]
    a = ""
    for x in sd:
        u = ord(x) - len(data)
        if u < 0:
            u = 0
        a += str(u)
    if len(a) < 8:
        while len(a) < 8:
            a += "0"
    b = 1
    for x in a:
        if len(str(b)) < 8:
            b *= ord(x)
        else:
            break
    c = str(b)
    if len(c) < 16:
        while len(c) < 16:
            c += c
    d = c[::-1]
    return d[:16]

def stepcrypt(data, key):
    raw_data = data
    encrypted_data = ""
    while len(raw_data) > 0:
        for k in key:
            if len(raw_data) > 0:
                character = ord(raw_data[0])
                offset = int(k)
                offset_character = character - offset
                if offset_character < 0:
                    encrypted_data += "0"
                else:
                    encrypted_data += chr(offset_character)
                raw_data = raw_data[1:]
            else:
                break

    return base64.b64encode(encrypted_data.encode("utf-8"))

def destepcrypt(data, key):
    encrypted_data = base64.b64decode(data).decode("utf-8")
    decrypted_data = ""
    while len(encrypted_data) > 0:
        for k in key:
            if len(encrypted_data) > 0:
                character = ord(encrypted_data[0])
                offset = int(k)
                offset_character = character + offset
                if offset_character > 127:
                    decrypted_data += "0"
                else:
                    decrypted_data += chr(offset_character)
                encrypted_data = encrypted_data[1:]
            else:
                break

    return decrypted_data

def writeCyphermap(data, filename, path):
    pixel_data = np.zeros((1024, 512, 3), dtype=np.uint8)
    raw_data = data
    block_count = len(raw_data) // 8

    for x in range(9):
        row_col_size = 2 ** x
        if math.sqrt(block_count) > row_col_size:
            continue
        else:
            block_width = 512 // row_col_size
            block_height = block_width * 2
            cell_size = block_width // 2

            # row_col_size rows of blocks in the cyphermap
            for rcy in range(row_col_size):
                # row_col_size columns of blocks in the cyphermap
                for rcx in range(row_col_size):
                        # 4 rows of cells per block
                        for by in range(4):
                            # 2 columns of cells per block
                            for bx in range(2):                                
                                if len(raw_data) > 0:
                                    if raw_data[0] == "1":
                                        # cell is cell_size tall                                       
                                        for cy in range(cell_size):
                                            # cell is cell_size wide
                                            for cx in range(cell_size):
                                                pixel_data[(rcy * block_height) + (by * cell_size) + cy, (rcx * block_width) + (bx * cell_size) + cx] = [255, 255, 255]
                                    raw_data = raw_data[1:]
                                else:
                                    break
            break

    iwrite(pixel_data, rf"{path}\{filename}.png")

def readCyphermap(path):
    raw_data = iread(path)

    # determine cell (and therefore block) size by reading pixels in rows until we get a pattern of black -> white or white -> black
    solved = False
    colours = []
    cell_pixel_count = 0
    index = 0

    while solved == False:
        current_pixel = raw_data[index][0]
        colours.append(current_pixel)

        if len(colours) > 0:
            if current_pixel != colours[index - 1]:
                solved = True
            else:
                cell_pixel_count += 1
        index += 1

    pixel_data = bitmapListTo2DArray(raw_data, 512)

    cell_size = cell_pixel_count
    row_col_size = (512 // cell_size) // 2  
    block_width = 512 // row_col_size
    block_height = block_width * 2
    binary_characters = ""

    # row_col_size rows of blocks in the cyphermap
    for rcy in range(row_col_size):
        # row_col_size columns of blocks in the cyphermap
        for rcx in range(row_col_size):
                # 4 rows of cells per block
                for by in range(4):
                    # 2 columns of cells per block
                    for bx in range(2):
                        if pixel_data[(rcy * block_height) + (by * cell_size)][(rcx * block_width) + (bx * cell_size)][0] == 0:
                            binary_characters += "0"
                        else:
                            binary_characters += "1"

    return binary_characters