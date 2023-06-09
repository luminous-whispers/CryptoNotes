# 0 心得
- 各种工作模式本身难度不大，填充和读入数据方式需要考虑封装抽象。以后将python复杂的数据类型读入和处理都封装起来，不管鲁棒性和复用性如何，简洁就行，我要被折磨出PTSD了。
- 工作模式主要分为分组密码和流密码模式，分组密码又分为有反馈和无反馈。两者的主要区别是分组密码借助SM4加解密模块实现加解密，流密码主要借助生成乱源流密钥进行加解密。SM4模块不是必须的，可以使用别的算法作为加解密模块。
- **后续优化：使用类对工作模式进行重新封装**

> 基础知识详见[链接模式](../链接模式.md)

# 1 源码
## ECB
```python
from sm4 import crypt
from basic import block_out, block_in
    
ENCRYPT = 1
DECRYPT = 0

def ecb():
    k = int(input().strip(), 16) 
    op = int(input()) # 模式
    # 读入明文流
    data = block_in(op)

    # 对每个数据块进行ECB模式加密/解密
    out = []
    for block in data:
        tmp = crypt(block, k, op)
        out.append(tmp)
    block_out(out, op)

ecb()
```

## CBC
```python
from sm4 import crypt
from basic import block_in, block_out

ENCRYPT = 1
DECRYPT = 0

def cbc():
    k = int(input().strip(), 16)
    IV = int(input().strip(), 16)
    op = int(input())
    data = block_in(op)

    last_c = IV
    out = []
    for i, block in enumerate(data):
        if op == ENCRYPT:
            c = crypt(last_c ^ block, k, op)
            out.append(c)

            # next chaos
            last_c = c

        elif op == DECRYPT:
            tmp = crypt(block, k, op)
            p = tmp^last_c
            out.append(p)

            last_c = block
    block_out(out, op)

cbc()
```

## CTR
```python
from basic import stream_in, stream_out
from sm4 import crypt

def ctr():
    k = int(input().strip(), 16)
    IV = int(input().strip(), 16)
    op = int(input())
    data, diff = stream_in() # diff代表了填充数量，加密结束去填充

    out = []
    cnt = IV
    for block in data:
        tmp = crypt(cnt, k, 1) #流密码加解密都采用Encrypt模块
        tmp = tmp ^ block
        # 计数器递增
        cnt += 1
        # 加入输出队列 
        out.append(tmp)
    stream_out(out, diff)


ctr()
```

## OFB
```python
from basic import stream_out, stream_in
from sm4 import crypt

def ofb():
    n = int(input())
    k = int(input().strip(), 16)
    IV = int(input().strip(), 16)
    op = int(input())
    data, diff = stream_in(n) 

    mask = (1 << 128)-1
    shift_reg = IV
    out = []
    for block in data:
        tmp = crypt(shift_reg, k, 1) # 流密码加解密都采用Encrypt模块
        tmp = tmp >> (128-n*8)

        # 更新移位寄存器（下次Enc输入）
        shift_reg = (shift_reg << n*8) & mask | tmp 

        # 流密钥加密
        tmp ^= block
        # 加入输出列表
        out.append(tmp)

    stream_out(out, diff, n)

ofb()
```

## CFB
```python
from basic import stream_out, stream_in
from sm4 import crypt

ENCRYPT = 1
DECRYPT = 0

def cfb():
    n = int(input())
    k = int(input().strip(), 16)
    IV = int(input().strip(), 16)
    op = int(input())
    data, diff = stream_in(n) 

    mask = (1 << 128)-1
    shift_reg = IV
    out = []
    for block in data:
        tmp = crypt(shift_reg, k, 1) # 流密码加解密都采用Encrypt模块
        tmp = tmp >> (128-n*8)
        tmp ^= block

        # 更新移位寄存器（下次Enc输入）
        if op == ENCRYPT:
            shift_reg = ((shift_reg << n*8) & mask) | tmp
        elif op == DECRYPT:
            shift_reg = (shift_reg << n*8) & mask | block

        # 加入输出列表
        out.append(tmp)
    stream_out(out, diff, n)

cfb()
```

## 输入输出及填充模块
basic.py
区分了流密码IO和分组密码IO，因为流密码输入都需要填充，输出都需要去填充；分组密码输入填充，输出去填充即可。当然可以写成一个函数，就是复杂些。
去填充原本写得较复杂，后来简化了（
```python
def int2hex(num, hex_width):
    """
    整数转为指定长度的十六进制字符串，不足补0
    >>> num2hex(1000, width=4)
    '0x03e8'
    :param int num
    :param width: width for hex str of num
    """
    return '0x{:0>{width}}'.format(hex(num)[2:].replace('L', ''),
                                 width=hex_width)


def pack(array, split_width=8):
    '''pack tuple of int into big int'''
    cnt = len(array)
    num = 0
    for i in range(cnt):
        num = (num << split_width) | array[i]
    return num

def unpack(num, full_width=32, split_width=8):
    '''unpack big int to int tuple, by bit width'''
    #要求输出full_width ，是因为对输出元组元素的个数有对齐要求， 比如含多前缀0的整型有时需拆解为(0,0,num1,num2)
    mask = (1 << split_width) - 1
    cnt = full_width // split_width
    array = []
    for _ in range(cnt):
        array.append(num & mask)
        num = num >> split_width
    array.reverse()
    return tuple(array)


def padding(data, block_size):
    '''
    对每个数据块进行填充，标准使用 PKCS#7 标准
    input: 
        block_size: number of bytes for each block           
        data: list of byte of data
    '''
    padding_size = block_size - len(data) % block_size
    padding = [padding_size] * padding_size
    data += padding
    return data

def unpadding(data, block_size):
    """
    去掉PKCS#7填充
    :param data: 需要去掉填充的数据
    :param block_size: 数据块大小
    :return: 去掉填充后的数据
    """
    padding_size = data[-1] # 获取最后一个字节的值
    # 去掉填充字节
    return data[:-padding_size]


import sys
def block_in(op=1, block_size=16):
    '''
    从stdin读入分组密码输入，并进行填充（block_size）
    :output: list of input block (128b * n)
    '''
    data = []
    for line in sys.stdin:
        line_data = [int(x, 16) for x in line.strip().split(" ")]
        data += line_data

    if op == SM4_ENCRYPT:
        data = padding(data, block_size)

    # 将data从按byte分组变为按block分组
    blocks = unpack(pack(data, 8), 8*len(data), 8*block_size)
    return blocks

def block_out(data, op=1, block_size=16):
    '''
    pad or unpad the data, output for block cipher
    :input: list of blocks to output (128b * n)
    '''
    tmp = []
    for block in data:
        # 拆成字节
        tmp += unpack(block, block_size*8, 8)

    if op == SM4_ENCRYPT:
        out = [int2hex(x, 2) for x in tmp]
    elif op == SM4_DECRYPT:
        # 去掉填充
        tmp = unpadding(tmp, block_size)
        out = [int2hex(x, 2) for x in tmp]

    for i, num in enumerate(out):
        print(num, end=' ')
        if (i+1) % 16 == 0:
            print("")
        # 本函数为测评要求，完全不必要


def stream_in(block_size=16):
    '''
    流密码读入，按block_size（/bytes）进行填充
    和分组密码输入区别是：加解密都要填充，
    return blocks, diff
    '''
    data = []
    for line in sys.stdin:
        line_data = [int(x, 16) for x in line.strip().split(" ")]
        data += line_data

    origin_len = len(data)
    data = padding(data, block_size)
    diff = len(data) - origin_len

    # 将data从按byte分组变为按block分组(流密码的异或组)
    blocks = unpack(pack(data, 8), 8*len(data), 8*block_size)
    return blocks, diff

def stream_out(data, stream_diff, block_size=16):
    '''
    流密码输出, 按diff去填充，block_size用于指定流密码分组长度(bytes)
    和分组密码输出区别是：加解密都要去填充，显式提供去填充的字节数
    '''
    tmp = []
    for block in data:
        # 拆成字节
        tmp += unpack(block, 8*block_size, 8)

    if stream_diff:
        # 显式去掉填充（用于流密码输出CTR）
        tmp = tmp[:-stream_diff] 
    out = [int2hex(x, 2) for x in tmp]

    for i, num in enumerate(out):
        print(num, end=' ')
        if (i+1) % 16 == 0:
            print("")
```

PKCS#7填充方法，标准实现：

```python
def padding(data, block_size):
    '''
    对每个数据块进行填充，标准使用 PKCS#7 标准
    input: 
        block_size: number of bytes for each block           
        data: list of byte of data
    '''
    padding_size = block_size - len(data) % block_size
    padding = [padding_size] * padding_size
    data += padding
    return data
    
def unpadding(data, block_size):
    """
    去掉PKCS#7填充
    :param data: 需要去掉填充的数据
    :param block_size: 数据块大小
    :return: 去掉填充后的数据
    """
    padding_size = data[-1] # 获取最后一个字节的值
     if padding_size > block_size or padding_size > len(data):
         # 填充不合法，抛出异常或者做其他错误处理
         raise ValueError("Invalid padding")

     # 检查填充字节是否合法
     padding = data[-padding_size:]
     for byte in padding:
         if byte != padding_size:
             # 填充不合法，抛出异常或者做其他错误处理
             raise ValueError("Invalid padding")

    # 去掉填充字节
    return data[:-padding_size]
```