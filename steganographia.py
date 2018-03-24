# coding=utf-8

from PIL import Image


def make_image_even(image):
    """
    取得一个 PIL 图像并且更改所有值为偶数（使最低有效位为 0）
    """
    pixels = list(image.getdata())
    even_pixels = [(r >> 1 << 1, g >> 1 << 1, b >> 1 << 1, a >> 1 << 1) for [r, g, b, a] in pixels] # 更改所有值为偶数
    even_image = Image.new(image.mode, image.size)
    even_image.putdata(even_pixels)
    return even_image


def const_len_bin(int):
    """
    内置函数 bin() 的替代，返回固定长度的二进制字符串
    """
    binary = "0"*(8-(len(bin(int))-2)) + bin(int).replace('0b', '') # 去掉 bin() 返回的二进制字符串中的'0b',并补足
    return binary


def encode_data_in_image(image, data):
    """
    将字符串编码到图片中
    """
    even_image = make_image_even(image)
    binary = ''.join(map(const_len_bin, bytearray(data, 'utf-8')))
    if len(binary) > len(image.getdata()) * 4:
        raise Exception("Error: Can't encode more than " + len(even_image.getdata())*4 + " bit in this image.")
    encode_pixels = [(r+int(binary[index*4+0]), g+int(binary[index*4+1]), b+int(binary[index*4+2]), a+int(binary[index*4+3]))
    if index*4 < len(binary) else (r, g, b, a) for index, (r, g, b, a) in enumerate(list(even_image.getdata()))]

    encode_image = Image.new(even_image.mode, even_image.size)
    encode_image.putdata(encode_pixels)
    return encode_image


def binary_to_string(binary):
    """
    从二进制字符串转为 UTF-8 字符串
    """
    index = 0
    string = []
    rec = lambda x, i: x[2:8] + (rec(x[8:], i-1) if i>1 else '') if x else ''
    fun = lambda x, i: x[i+1:8] + rec(x[8:], i-1)
    while index + 1 < len(binary):
        chartype = binary[index:].index('0')
        length = chartype*8 if chartype else 8
        string.append(chr(int(fun(binary[index:index+length], chartype), 2)))
        index += length
    return ''.join(string)


def decode_image(image):
    """
    解码隐藏数据
    """
    pixels = list(image.getdata())  # 获得像素列表
    binary = ''.join([str(int(r>>1<<1!=r))+str(int(g>>1<<1!=g))+str(int(b>>1<<1!=b))+str(int(t>>1<<1!=t)) for (r,g,b,t) in pixels]) # 提取图片中所有最低有效位中的数据
    # 找到数据截止处的索引
    location_double_null = binary.find('0000000000000000')
    end_index = location_double_null+(8-(location_double_null % 8)) if location_double_null%8 != 0 else location_double_null
    data = binary_to_string(binary[0:end_index])
    return data


if __name__ == "__main__":
    encode_data_in_image(Image.open("test.png"), 'hello world').save('encodeImage.png')
    print(decode_image(Image.open("encodeImage.png")))
