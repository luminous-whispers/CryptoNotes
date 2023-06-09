## BBS发生器

#重点 

BBS (Blum-Blum-Shub) 是**密码安全伪随机数比特发生器**, 有安全性和输出随机性依赖于模数 $n=p\times q$ 的平方剩余特性. 如果 $p,\ q$ 皆形如 $4x+3$, 那么它们满足以下性质:
1. $p$ 和 $q$ 都有唯一二次剩余, 即 $n=p\times q$ 的二次剩余数量非常有限
2. 周期长度理论上可达到 $\frac{1}{4}\cdot p\cdot q$, 即可生成较长不重复序列, 安全性高. 

算法流程如下:
- 选取大素数 $p,\ q$, 满足 $p\equiv q\equiv 3\pmod{4}$
- 计算 $n=p\times q$
- 选取随机数 $seed$, 要求 $seed$ 和 $n$ 互素.
- 按以下算法产生比特序列 $\{B_{i}\}$  
$X_{0}=seed^{2}\pmod{n}$  
$For\quad i=1\quad to\quad \infty:$  
$\qquad X_{i}=X_{i-1}^{2}\pmod{n}$  
$\qquad B_{i}=X_{i}\quad\pmod{2}$