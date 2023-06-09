## 1 共模攻击
*生成秘钥的过程中使用了相同的模数, 此时用不同的公钥e加密同一信息m不安全.* 

### 原理:
$$c1 = m^{e1}\ (mod\ N)$$
$$c2 = m^{e2}\ (mod\ N)$$

若两个公钥e互素，根据扩展的欧几里得算法则存在s1, s2有:

$$e1 * s1 + e2 * s2\ =\ gcd(e1,\ e2)\ =\ 1$$

可得：

$$
\begin{aligned}
&(c1^{s1}\ *\ c2^{s2})mod\ N\\
=&\ (m^{e1}\ (mod\ N))^{s1}\ *\ (m^{e2}\ (mod\ N))^{s2}\ (mod\ N)\\
=&\ m^{(e1 * s1\ +\ e2 * s2)}\ (mod\ N)\\
=&\ m\ (mod\ N)\\
=&\ m \\
\end{aligned}
$$

也就是在完全不知道私钥的情况下，得到了明文m

$$
m = (c1^{s1}\ *\ c2^{s2})\ mod\ N
$$

## 2 密钥泄露
*若某私钥d被泄露，则基于该 $(p, q)$ 的所有公私钥对 $(e, d)$ 都会不安全*

建议使用不同 $p,q$ 生成不同的密钥.

### 原理:

假设 $p,q$ 生成了两对公私钥对: $(e_{1},d_{1})$, $(e_{2},d_{2})$, 其中 $d_{1}$ 泄露. 攻击手段如下:

1. 在公开信道获取公钥 $e_{1}$, $e_{2}$
2. $e_{1}\times d_{1}\equiv 1\ \pmod{\phi(n)}$, 其中 $\phi(n)=(p-1)\times(q-1)$. 注意仅知道 $d_{1}\cdot e_{1}\equiv k\cdot\phi(n)$, 而不知道 $\phi(n)$.
3. 计算 $d_{2}\equiv e_{2}^{-1}\pmod{e_{1}\times d_{1}-1}\equiv e_{2}^{-1}\pmod{\mathbf{k}\cdot \phi(n)}$. 等价于 $d_{2}\equiv e_{2}^{-1}\pmod{\phi{(n)}}$.
