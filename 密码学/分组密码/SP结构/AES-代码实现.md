# 0 心得

- 严重怀疑测评机没有处理好 windows平台换行符`\r\n`与linux换行符不兼容 的问题, 输入函数必须加上strip()去掉空白字符, 否则报错RE

- 减少了使用复杂的列表推导式, 尤其是二维的推导式. 这东西看上去简洁, 实则会大幅增加 写和阅读代码 的难度. 写一个双重循环真的不费事, 看起来不geek罢了.

- 解密部分, 采取同结构解密方式, 并不会提高代码复用的程度, 相反增加了数据处理的难度. 对于python这种弱类型语言, 这种数据处理无疑比设计代码结构更加折磨人.


# 1 说明文档

> copyright: 该文档是chatGPT-4模型自动生成的, 无版权


**密码学第四次实验 AES及其相关实现 2023-3**

AES-128加密算法的实现及其组成部分。代码包含以下几个模块：

1. 密钥生成（key_expansion.py）
2. 加密和解密操作（aes.py）
3. 有限域运算（gf.py）
4. 常量和置换盒（constant.py）

## 密钥生成

文件名：key_expansion.py

密钥生成模块负责将初始密钥扩展为轮密钥。提供了以下几个功能函数：

- `sub_word(w)`
- `rot_word(w)`
- `xor_word(w1, w2)`
- `key_expansion(in_key)`

`key_expansion` 函数接收一个初始密钥（4 * Nk字节），并生成Nb * (Nr + 1)字节的轮密钥。这些轮密钥将用于加密和解密操作。

## 加密和解密操作

文件名：aes.py

加密和解密操作模块提供了AES加密算法的核心功能。包括以下几个功能函数：

- `add_round_key(state, key)`
- `sub_bytes(state, op=1)`
- `shift_rows(state, op=1)`
- `mix_columns(state, op=1)`
- `dec(in_block, rkey)`
- `enc(in_block, rkey)`

### 加密

`enc` 函数负责将输入数据块（4 * Nb字节）加密。它接收输入数据块和轮密钥（由`key_expansion`生成），并输出加密后的数据块。

加密过程包括以下几个步骤：

1. 将输入数据块转换为状态矩阵
2. 执行Nr次轮操作，包括：
   - 字节代换（`sub_bytes`）
   - 行移位（`shift_rows`）
   - 列混淆（`mix_columns`，除最后一轮外）
   - 轮密钥加（`add_round_key`）
3. 将加密后的状态矩阵转换回输出数据块

### 解密

`dec` 函数负责将加密后的数据块（4 * Nb字节）解密。它接收加密后的数据块和轮密钥（由`key_expansion`生成），并输出解密后的数据块。

(函数op代表是该函数的逆操作)

解密过程与加密过程相反，包括以下几个步骤：

1. 将加密后的数据块转换为状态矩阵
2. 执行Nr次轮操作，包括：
   - 逆字节代换（`sub_bytes`，参数op为0）
   - 逆行移位（`shift_rows`，参数op为0）
   - 逆列混淆（`mix_columns`，参数op为0，除最后一轮外）
   - 轮密钥加（`add_round_key`）
3. 将解密后的状态矩阵转换回输出



# 2 详细代码

#面向过程

- cipher.py 加解密主体

```python
import gf
import key
import constant as Con

def add_round_key(state, key):
    '''add round key'''
    for w in range(Con.Nb):
        for byte in range(4):
            state[w][byte] ^= key[w][byte]

def sub_bytes(state, op=1):
    '''substitute bytes'''
    if op :
        sbox = Con.s_box
    else:
        sbox = Con.inv_s_box
    for w in range(Con.Nb):
        for byte in range(4):
            state[w][byte] = sbox[state[w][byte] >> 4][state[w][byte] & 0xF]

def shift_rows(state, op=1):
    '''shift rows'''
    if op :
        for r in range(1, 4):  # row, 但state是按列存储的
            for _ in range(r):  # 循环移位次数
                for i in range(3):  # 循环移位
                    state[i][r], state[i+1][r] = state[i+1][r], state[i][r]
    else:
        for r in range(1, 4):  # row, 但state是按列存储的
            for _ in range(r):  # 循环移位次数
                for i in range(3, 0, -1):  # 循环移位
                    state[i][r], state[i-1][r] = state[i-1][r], state[i][r]

def mix_columns(state, op=1):
    '''mix columns'''
    if op :
        state[:] = gf.mul_matrix(state, Con.mix_matrix)  # 这里使用切片来访问原列表地址, 否则不会改变原地址内容, 而是交换指针
    else:
        state[:] = gf.mul_matrix(state, Con.inv_mix_matrix)  

def dec(in_block, rkey):
    '''
    decryption for in_block data
    Input:
        in_block: list of 4*Nb bytes, split as byte
        rkey: list of (Nr+1)*Nb*4 bytes from key_expansion, split as word
    Output:
        out_block: list of 4*Nb bytes
    '''
    # state: w0, w1, w2, w3
    state = [[0] * 4 for _ in range(Con.Nb)]
    for w in range(Con.Nb):
        for byte in range(4):
            state[w][byte] = in_block[4*w + byte]

    add_round_key(state, rkey[Con.Nr * Con.Nb:])
    for round in range(Con.Nr-1, 0, -1):
        sub_bytes(state, 0)
        shift_rows(state, 0)
        add_round_key(state, rkey[round*Con.Nb: (round+1)*Con.Nb])
        mix_columns(state, 0)
    # last round
    sub_bytes(state, 0)
    shift_rows(state, 0)
    add_round_key(state, rkey[:Con.Nb])

    out_block = [0] * 4 * Con.Nb
    for w in range(Con.Nb):
        for b in range(4):
            out_block[w*4+b] = state[w][b]
    return out_block


def enc(in_block, rkey):
    '''
    encryption for in_block data
    Input:
        in_block: list of 4*Nb bytes, split as byte
        rkey: list of (Nr+1)*Nb*4 bytes from key_expansion, split as word
    Output:
        out_block: list of 4*Nb bytes
    '''
    # state: w0, w1, w2, w3
    state = [[0] * 4 for _ in range(Con.Nb)]
    for w in range(Con.Nb):
        for byte in range(4):
            state[w][byte] = in_block[4*w + byte]

    add_round_key(state, rkey[0: Con.Nb])
    for round in range(1, Con.Nr):
        sub_bytes(state)
        shift_rows(state)
        mix_columns(state)
        add_round_key(state, rkey[round*Con.Nb: (round+1)*Con.Nb])
    # last round
    sub_bytes(state)
    shift_rows(state)
    add_round_key(state, rkey[Con.Nr * Con.Nb:])

    out_block = [0] * 4 * Con.Nb
    for w in range(Con.Nb):
        for b in range(4):
            out_block[w*4+b] = state[w][b]
    return out_block
```

- key.py 密钥扩展

```python
import constant as c

def sub_word(w):
    sbox = c.s_box
    for i, v in enumerate(w):
        w[i] = sbox[v>>4][v&0xF]
    return w

def rot_word(w):
    return w[1:] + w[:1]

def xor_word(w1, w2):
    return [b1^b2 for b1, b2 in zip(w1, w2)]

def key_expansion(in_key):
    '''
    AES key expansion for round keys
    Input:
        in_key: input initial key 4*Nk bytes, split as byte
    Output:
        round_key: Nb*(Nr+1) bytes for 4 bytes as a w, split as word(4 bytes)
    '''
    words = [in_key[4*i:4*(i+1)] for i in range(c.Nk)]

    for i in range(c.Nk, c.Nb * (c.Nr+1)):
        tmp = words[i-1] #! 复制了地址，可变类型不复制对象，后面被坑了
        if (i % c.Nk) == 0:
            tmp = xor_word(sub_word(rot_word(tmp[:])), c.Rcon[i//c.Nk-1])
        elif (c.Nk > 6) and (i % c.Nk == 4): #为了向后兼容更高位加密
            tmp = sub_word(tmp[:])
        words.append(xor_word(words[i-c.Nk], tmp))

    return words
```

- constant.py 存放常量

```python
'''constant: for AES-128'''
Nk = 4
Nb = 4
Nr = 10

Rcon = [
    b'\x01\x00\x00\x00', b'\x02\x00\x00\x00', 
    b'\x04\x00\x00\x00', b'\x08\x00\x00\x00', 
    b'\x10\x00\x00\x00', b'\x20\x00\x00\x00', 
    b'\x40\x00\x00\x00', b'\x80\x00\x00\x00', 
    b'\x1b\x00\x00\x00', b'\x36\x00\x00\x00'] 

mix_matrix = (
    (2, 1, 1, 3),
    (3, 2, 1, 1),
    (1, 3, 2, 1),
    (1, 1, 3, 2)
)

inv_mix_matrix = (
    (0x0e, 0x09, 0x0d, 0x0b),
    (0x0b, 0x0e, 0x09, 0x0d),
    (0x0d, 0x0b, 0x0e, 0x09),
    (0x09, 0x0d, 0x0b, 0x0e)
)

s_box = [
[ 0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76 ],
[ 0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0 ],
[ 0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15 ],
[ 0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75 ],
[ 0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84 ],
[ 0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf ],
[ 0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8 ],
[ 0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2 ],
[ 0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73 ],
[ 0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb ],
[ 0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79 ],
[ 0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08 ],
[ 0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a ],
[ 0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e ],
[ 0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf ],
[ 0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16 ],
]
inv_s_box = [
[ 0x52, 0x09, 0x6a, 0xd5, 0x30, 0x36, 0xa5, 0x38, 0xbf, 0x40, 0xa3, 0x9e, 0x81, 0xf3, 0xd7, 0xfb ],
[ 0x7c, 0xe3, 0x39, 0x82, 0x9b, 0x2f, 0xff, 0x87, 0x34, 0x8e, 0x43, 0x44, 0xc4, 0xde, 0xe9, 0xcb ],
[ 0x54, 0x7b, 0x94, 0x32, 0xa6, 0xc2, 0x23, 0x3d, 0xee, 0x4c, 0x95, 0x0b, 0x42, 0xfa, 0xc3, 0x4e ],
[ 0x08, 0x2e, 0xa1, 0x66, 0x28, 0xd9, 0x24, 0xb2, 0x76, 0x5b, 0xa2, 0x49, 0x6d, 0x8b, 0xd1, 0x25 ],
[ 0x72, 0xf8, 0xf6, 0x64, 0x86, 0x68, 0x98, 0x16, 0xd4, 0xa4, 0x5c, 0xcc, 0x5d, 0x65, 0xb6, 0x92 ],
[ 0x6c, 0x70, 0x48, 0x50, 0xfd, 0xed, 0xb9, 0xda, 0x5e, 0x15, 0x46, 0x57, 0xa7, 0x8d, 0x9d, 0x84 ],
[ 0x90, 0xd8, 0xab, 0x00, 0x8c, 0xbc, 0xd3, 0x0a, 0xf7, 0xe4, 0x58, 0x05, 0xb8, 0xb3, 0x45, 0x06 ],
[ 0xd0, 0x2c, 0x1e, 0x8f, 0xca, 0x3f, 0x0f, 0x02, 0xc1, 0xaf, 0xbd, 0x03, 0x01, 0x13, 0x8a, 0x6b ],
[ 0x3a, 0x91, 0x11, 0x41, 0x4f, 0x67, 0xdc, 0xea, 0x97, 0xf2, 0xcf, 0xce, 0xf0, 0xb4, 0xe6, 0x73 ],
[ 0x96, 0xac, 0x74, 0x22, 0xe7, 0xad, 0x35, 0x85, 0xe2, 0xf9, 0x37, 0xe8, 0x1c, 0x75, 0xdf, 0x6e ],
[ 0x47, 0xf1, 0x1a, 0x71, 0x1d, 0x29, 0xc5, 0x89, 0x6f, 0xb7, 0x62, 0x0e, 0xaa, 0x18, 0xbe, 0x1b ],
[ 0xfc, 0x56, 0x3e, 0x4b, 0xc6, 0xd2, 0x79, 0x20, 0x9a, 0xdb, 0xc0, 0xfe, 0x78, 0xcd, 0x5a, 0xf4 ],
[ 0x1f, 0xdd, 0xa8, 0x33, 0x88, 0x07, 0xc7, 0x31, 0xb1, 0x12, 0x10, 0x59, 0x27, 0x80, 0xec, 0x5f ],
[ 0x60, 0x51, 0x7f, 0xa9, 0x19, 0xb5, 0x4a, 0x0d, 0x2d, 0xe5, 0x7a, 0x9f, 0x93, 0xc9, 0x9c, 0xef ],
[ 0xa0, 0xe0, 0x3b, 0x4d, 0xae, 0x2a, 0xf5, 0xb0, 0xc8, 0xeb, 0xbb, 0x3c, 0x83, 0x53, 0x99, 0x61 ],
[ 0x17, 0x2b, 0x04, 0x7e, 0xba, 0x77, 0xd6, 0x26, 0xe1, 0x69, 0x14, 0x63, 0x55, 0x21, 0x0c, 0x7d ],
]
```

- gf.py 实现有限域上的运算

AES中对有系数多项式和{0,1}系数多项式有区分, {0,1}系数多项式是在$GF(2^8)$上进行运算, 用来生成F的不可约多项式为$x^8+x^4+x^3+x+1$. 而有系数多项式进行乘法时, 系数(一字节长度)运算视作$GF(2^8)$上的多项式运算(每bit代表一个系数), 而多项式次数通过$x^i\ (mod\ x^4+1)=x^{i\ mod\ 4}$来压缩.

下面是有系数多项式乘法的演示: 

$c\left(x\right)\\=a(x)*b(x)\\=c_6x^6+c_5x^5+c_4x^4+c_3x^3+c_2x^2+c_1x+c_0$


$\begin{cases}c_0=a_0\ast b_0\\ c_6=a_3\ast b_3\\ c_1=a_1\ast b_0\oplus a_0\ast b_1\\c_5=a_3\ast b_2\oplus a_2\ast b_3\\c_2=a_2\ast b_0\oplus a_1\ast b_1\oplus a_0\ast b_2\\ c_4=a_3\ast b_1\oplus a_2\ast b_2\oplus a_1\ast b_3\\ c_3=a_3\ast b_0\oplus a_2\ast b_1\oplus a_1\ast b_2\oplus a_0\ast b_3\end{cases}$

$d\left(x\right)\\=c\left(x\right)mod\left(x^4+1\right)\\=c_3x^3+\left(c_6\oplus c_2\right)x^2+\left(c_5\oplus c_1\right)x+\left(c_4\oplus c_0\right)$

> **后续改成链接， 有限域运算改成单独章节**

```python
irred_poly = 0b100011011

def add_or_sub(x_bin, y_bin):
    return x_bin ^ y_bin

def mul(x_bin, y_bin):
    '''x*y on the GF(2^8), with modulo irred_poly'''
    z_bin = 0
    for i in range(8):
        if y_bin & (1 << i):
            z_bin ^= x_bin << i
    # mod irreducible poly
    for i in range(14, 7, -1):
        if z_bin & (1 << i):
            z_bin ^= (irred_poly << (i - 8))
    return z_bin

def mod_div(x_bin, y_bin):
    '''x /mod y, return q, r. on the GF(2)[x]'''
    q = 0; r = x_bin
    r_deg = len(bin(r)) -3
    y_deg = len(bin(y_bin)) -3

    while y_deg <= r_deg:
        q = q ^ (1 << (r_deg-y_deg))
        r = r ^ (y_bin << (r_deg-y_deg))
        if y_bin and not r:
            #此情况，由于y=1的位数已经最低，所以r位数不可能更低了. r=0时退出即可
            break
        r_deg = len(bin(r)) -3 #自动去掉前缀0，即自动缩减到当前最高位
    return (q, r)

def fast_power(num, exp):
    '''num^exp , on the GF(2^8) with irred_poly 0b11b'''
    ans = 1
    base = num
    while exp != 0:
        if exp & 1 != 0:
            ans = mul(base, ans)
        base = mul(base, base)
        exp >>= 1
    _, r = mod_div(ans, irred_poly)
    return r

def exGCD(x, y):
    '''return s, t, gcd, such that s*x + t*y = gcd'''
    d, s, t = y, 0, 1
    d1, s1, t1 = x, 1, 0
    while d != 0:
        q, r = mod_div(d1, d)
        d1, d = d, r
        s1, s = s, s1 ^ mul(q, s)
        t1, t = t, t1 ^ mul(q, t)

    return s1, t1, d1

def find_inverse(a, m):
    x, _, _ = exGCD(a, m)  # 并没有检查两者是否互素
    return x

def mul_matrix(A, B):
    '''矩阵乘法, A*B'''
    r = len(A)
    c = len(B[0])
    assert len(A[0]) == len(B), 'invalid matrix form'

    C = [[0 for j in range(c)] for i in range(r)] # 初始化C的内存
    for i in range(r):
        for j in range(c):
            for k in range(len(B)):
                C[i][j] = add_or_sub(C[i][j], mul(A[i][k], B[k][j]))
    return C
```


