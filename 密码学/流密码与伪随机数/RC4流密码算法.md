## RC4算法

RC4, Rivest Cipher 4, 是一种[**流密码**](流密码.md)算法, 由Ron Rivest设计. 简单高效, 但近年来发现一些安全漏洞. 其在速度上比较AES高效软件实现已不占优.

RC4用一S表生成序列密钥, 主要步骤一是**密钥调度算法** (KSA), 使用初始密钥生成S表; 二是**伪随机数生成算法** (PRGA), 利用S表生成伪随机数序列.

### 1 密钥调度算法

KSA, Key Scheduling Algorithm, 使用初始密钥完成S表初始化. 

初始密钥长度应小于等于256字节, KSA算法将其扩展为调度表(S表), S表是256维向量, 分量长1字节. 实现过程如下:

0. 初始化两计数器 $i=0$, $j=0$
1. $S[i]=i,\ 0\leq i\lt 255$, 线性填充
2. $For\quad i\ = 0\ \to 255:$  
	$\quad j=j+S[i]+K[i\pmod{256}]\pmod{256}$, K为字节串初始密钥.  
	$\quad Swap(\ S[i],\ S[j]\ )$

### 2 伪随机数生成算法

PRGA, Pseudo-Random Generation Algorithm, 生成和明文等长**字节密钥流**.

1. 初始化计数器 $i=0$, $j=0$
2. 如下生成随机字节:  
	- $i=i+1\pmod{256}$  
	- $j=j+S[i]\pmod{256}$  
	- $Swap(\ S[i],\ S[j]\ )$  
	- $t=S[i]+S[j]\pmod{256}$  
	- $Ks=S[t]$, 输出字节.