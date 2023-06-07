AES (Advanced Encryption Standard) 是NIST于2001年选定的, 用于替代DES的算法.

AES以**Rijndael迭代型密码算法**为基础, 但分组长度固定为128`bits`, 仅允许密钥长度可变(128`bits`, 192`bits`, 256`bits`).

![|250](../../../attach/Pasted%20image%2020230607164020.png)

## AES 构造

**长度**:  
word, 字, 32`bits`   
state, 内部状态:
```
state={
	byte11, byte12, byte13, byte14, // word 1
	byte21, byte22, byte23, byte24,
	byte31, byte32, byte33, byte34,
	byte41, byte42, byte43, byte44
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
==为了让加解密结构更加类似, AES最后一轮没有 `MixColumns`.== 原理一见[代换置换网络](代换置换网络.md), 二需理解 `SubBytes` 和 `ShiftRows` 结构可以互换位置, 因为 `ShiftRows` 不改动字节内部.
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

## AES 评价

实现方便简洁, 同时不失安全性.  
...