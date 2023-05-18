## RSA密码体系
RSA公钥体系基于大素数分解的NPC困难问题：

**对于大素数N，
如果其可被分解为两素数(记为素数p、q); 并且存在e和$\phi(N)$互素 (记, d是e关于模$\phi(N)$的逆元)。
那么 $x^{e}\equiv c\ \   (mod\; N)$ 有解 $x\equiv c^{d}\ \ (mod\; N)$**

> 区别加密和签名的概念可以参见: [RSA签名和加密](RSA签名和加密.md)

### 1 加解密原理

- 场景：A需要给B发送加密信息，但A似乎不方便保存密码。
- 加密通讯流程:
  1. B方生成密钥, 在公共频道公开公钥对(e, N), 自己保留私钥d
  2. A方接收公钥对(e, N), 对自己要发送给B的消息msg进行加密: $cipher \equiv msg^{e}\;(mod\ N)$, 并发送给B
  3. B接收到密文cipher，进行解密：$msg \equiv cipher^{d}\ (mod\ N)$

### 2 数字签名原理

- 场景：A需要给B发送消息，消息不怕泄露，但害怕被篡改。换言之，通过数字签名，可以防止消息被篡改，但消息本身对攻击者也是可见的。
- 签名通讯流程: 
  1. A方生成密钥, 在公共频道公开公钥(e, N), 自己保留私钥d
  2. A方对消息msg进行加签, 以防篡改: $signature \equiv msg^{d}\; (mod\ N)$, 并将签名和消息本身(signature, msg)都发送给B
  3. B通过公钥e进行验签, 即检验signature验签结果是否和msg一致, 如果一致就说明msg未被篡改: $msg' \equiv signature^{d}\; (mod\ N)$, check $msg'\equiv msg$
     
### 3 算法加速

#### 利用p、q加速解密

利用已知信息p、q加速算法解密信息的过程。这是因为通常d相对e来说比较大，因此解密成本比加密成本高。
优化步骤：

1. 利用N=q\*p，将解密等式化简为方程组
   $m \equiv c^{d}\ (mod\ N)$

$\Longleftrightarrow\begin{cases}m_{1}\equiv c^{d}\ (mod\ p)\\m_{2}\equiv c^{d}\ (mod\ q)\end{cases}$

$\Longleftrightarrow\begin{cases}m_{1}\equiv (c\ \ mod\,p )^{d\ (mod\;p-1)}\ (mod\ p)\\m_{2}\equiv (c\ \ mod\,q)^{d\ (mod\;p-1)}\ (mod\ q)\end{cases}$

2. 利用**中国剩余定理**计算方程组
   
   >  见[中国剩余定理](../../../代数/中国剩余定理.md)

#### 等效模数

求解d时, 可以利用等效的模数加速求逆. 这基于以下的推论:
$$d*e \equiv 1\ (mod\ (p-1)*(q-1)) \Longleftrightarrow d*e\equiv 1\ (mod\ \frac{(p-1)*(q-1)}{g})$$
其中, $g\ =\ Gcd(p-1,\ q-1)$
两者d等效, 但比正常方法求得的d小, 计算时速度更快. 这也说明了, d不是对模数唯一的.
*(当然, 代价是密钥d安全性也下降了, 所以当g过大时, 需要重新选择合适的pq, 防止d过小)*

#### 数学加速
- 见[扩展欧几里得算法](../../../代数/扩展欧几里得算法.md)求最大公因子和逆元
- 见[快速模幂算法](../../../代数/快速模幂算法.md)

### 4 安全性分析

> 参考[合数分解](attack/合数分解.md)