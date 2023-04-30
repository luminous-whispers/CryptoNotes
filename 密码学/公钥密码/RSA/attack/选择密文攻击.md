: Plain-RSA 教科书式RSA. 
: CCA choice ciphertext attack 选择密文攻击


CCA是针对Plain-RSA的有效攻击手段, 但经过OAEP等引入随机的填充方式后, 能够有效防御.

### 攻击流程
假设密文 $C$ 和明文 $M$, 选取随机数r. 
此时敌手已知 $(C, e, N, r)$

1. 让A解密$r^eC$. 因为$r^eC=r^eM^e$, 所以解密结果为$rM$, CCA假定敌手可以获得解密值
2. 计算 $r^{-1}\ \%\ n$
3. 计算 $M=r^{-1}\times rM\ \%\ n$