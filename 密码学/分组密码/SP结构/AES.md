[AES](../../文档/AES-standard.pdf) (Advanced Encryption Standard) 是NIST于2001年选定的, 用于替代DES的算法.

AES以**Rijndael迭代型密码算法**为基础, 但分组长度固定为128`bits`, 仅允许密钥长度可变(128`bits`, 192`bits`, 256`bits`).

![|250](../../../attach/Pasted%20image%2020230607164020.png)

## AES 构造

**长度**:  
word, 字, 32`bits`   
state, 内部状态:
```
state={
	byte1, byte5, byte9, byte13, // word1
	byte2, byte6, byte10, byte14,
	byte3, byte7, byte11, byte15,
	byte4, byte8, byte12, byte16
}
```

**常数**:  
`Nb`: 分组字长度, AES中固定为4, Rijndael中可变.  
`Nr`: 轮数, 建议10以上.  
`Nk`: 密钥字长度, 可为4/6/8. 随着密钥长度变化, 密钥扩展算法略有不同.

### 1 单轮结构
AES是迭代型结构, 每轮结构如下:
```
Round{
	SubBytes( State ) // S盒变换
	ShiftRows( State ) // 行移位
	MixColumns( State ) // 列混淆
	AddRoundKey( State, RoundKey ) // 轮密钥加
}
```

#### 1.1 字节替换

见[AES-SBox](AES-SBox.md)

#### 1.2 行移位 `ShiftRows`
线性变换
$$
State=
\begin{bmatrix}
B_{00} & B_{01} & B_{02} & B_{03} \\
B_{10} & B_{11} & B_{12} & B_{13} \\
B_{20} & B_{21} & B_{22} & B_{23} \\
B_{30} & B_{31} & B_{32} & B_{33}
\end{bmatrix}
\longrightarrow
\begin{bmatrix}
B_{00} & B_{01} & B_{02} & B_{03} \\
B_{11} & B_{12} & B_{13} & B_{10} \\
B_{22} & B_{23} & B_{20} & B_{21} \\
B_{33} & B_{30} & B_{31} & B_{32}
\end{bmatrix}
\begin{matrix}
 & \\
\Leftarrow &\text{ring shift left 1}\\
\Leftarrow &\text{ring shift left 2} \\
\Leftarrow & \text{ring shift left 3} 
\end{matrix}
$$

#### 1.3 列混淆 `MixColumns`
$$
\begin{bmatrix}
0x02 & 0x03 & 0x01 & 0x01 \\
0x01 & 0x02 & 0x03 & 0x01 \\
0x01 & 0x01 & 0x02 & 0x03 \\
0x03 & 0x01 & 0x01 & 0x02
\end{bmatrix}\cdot
State=State'
$$
注意, 运算定义在 $GF(2^8)$上.
对于逆运算:
$$
\begin{bmatrix}
0x02 & 0x03 & 0x01 & 0x01 \\
0x01 & 0x02 & 0x03 & 0x01 \\
0x01 & 0x01 & 0x02 & 0x03 \\
0x03 & 0x01 & 0x01 & 0x02
\end{bmatrix}^{-1}
=
\begin{bmatrix}
0x0E & 0x0B & 0x0D & 0x09 \\
0x09 & 0x0E & 0x0B & 0x0D \\
0x0D & 0x09 & 0x0E & 0x0B \\
0x0B & 0x0D & 0x09 & 0x0E
\end{bmatrix}
$$

另一种理解方式: 将状态列视为 $GF(2^{8})$上的多项式 $a(x)$ (和同样定义在 $GF(2^{8})$上的系数区分), 则结果 $b(x)=a(x)\cdot c(x)\pmod{x^{4}+1}$, $c(x)=03x^{3}+01x^{2}+01x+02$.

注意, 列混淆是SP网络中的**代换**操作, 因为不是纯调换顺序.

#### 1.4 轮密钥加 `AddRoundKey`

密钥填入顺序:
$$
InitKey=
\begin{bmatrix}
B_{0} & B_{4} & B_{8} & B_{12} \\
B_{1} & B_{5} & B_{9} & B_{13} \\
B_{2} & B_{6} & B_{10} & B_{14} \\
B_{3} & B_{7} & B_{11} & B_{15}
\end{bmatrix}
=
\begin{pmatrix}
w_{1} & w_{2} & w_{3} & w_{4}
\end{pmatrix}
$$

轮密钥加:
$$
State \oplus RoundKey_{i} = 
\begin{pmatrix}
sw_{1}\oplus kw_{1}, & sw_{2}\oplus kw_{2}, & sw_{3}\oplus kw_{3}, & sw_{4}\oplus kw_{4}
\end{pmatrix}
$$

### 2 Rijndael 整体结构

加密结构:
```
Rijndal( State, Key ){
	RoundKey <- KeyExpansion( Key );
	AddRoundKey( State, RoundKey[0] );
	For i from 1 to Nr-1:
		SubBytes( State );
		ShiftRow( State );
		MixColumn( State );
		AddRoundKey( State, RoundKey[i] );
	EndFor
	SubBytes( State );
	ShiftRow( State );
	AddRoundKey( State, RoundKey[r] );
}
```

解密结构:
```
Rijndal( State, Key ){
	RoundKey <- KeyExpansion( Key );
	AddRoundKey( State, RoundKey[r] );
	InvShiftRow( State );
	InvSubBytes( State );
	For i from 1 to Nr-1:
		AddRoundKey( State, RoundKey[i] );
		InvMixColumn( State );
		InvShiftRow( State );
		InvSubBytes( State );
	EndFor
	AddRoundKey( State, RoundKey[0] );
}
```

等效解密结构:  
==为了让加解密结构更加类似, AES最后一轮没有 `MixColumns`.== 原理一见[代换置换网络](代换置换网络.md), 即`MixColumn`和`AddRoundKey`可在某些条件下互换位置; 二需理解 `SubBytes` 和 `ShiftRows` 结构可互换位置, 因为 `ShiftRows` 不改动字节内部.

```
Rijndal( State, Key ){
	RoundKey <- KeyExpansion( Key );
	AddPermutateRoundKey( State, RoundKey[r] );
	For i from 1 to Nr-1:
		InvSubBytes( State );
		InvShiftRow( State );
		InvMixColumn( State );
		AddPermutateRoundKey( State, RoundKey[i] );
	EndFor
	InvSubBytes( State );
	InvShiftRow( State );
	AddPermutateRoundKey( State, RoundKey[0] );
}
```

### 3 密钥扩展

`Nk=4`时密钥扩展步骤如下, `Nk`增长时, 会有些许变化, 详见[AES标准](../../文档/AES-standard.pdf).

![|550](../../../attach/Pasted%20image%2020230608165056.png)

变换 $g$详情如:
1. 循环左移一字节
2. 用[Sbox](AES-SBox.md)进行字节替代
3. 与轮常数 `Rcon[i]` 异或.   
其中, $Rcon[i]=(RC[i], 0x00, 0x00, 0x00)$, $RC[i]=2^{i-1}$.

==洒家对g的作用还没有深刻理解.== 应该和抗差分分析有一定关系.

## AES 分析

Rijndael算法高性能, 高效率, 高伸缩性, 存储要求低. 缺点是加解密区别较大, 硬件重用较困难.  
AES雪崩效应比DES佳, 因此轮数也少, 10轮AES安全性已非常高, 最有效破解方案是密钥穷举.

字节扩散效果:
![|450](../../../attach/Pasted%20image%2020230608144829.png)

比特扩散效果:  
...
