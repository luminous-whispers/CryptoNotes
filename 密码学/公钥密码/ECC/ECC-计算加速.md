标量乘的性能衡量ECC加密性能的重要指标.  
标量乘由点加组成, 点加主要瓶颈在于**模幂**和**模除 (模逆)** 运算

优化标量乘方法大致有三类:  
- *优化标量乘流程*: 优化$[k]P$计算流程, 如快速模幂算法/NAF窗口方法/多基链/加法链
- *转换坐标系*: 普通二元坐标系, Add运算需要1模逆+3模乘, Double运算需要1模逆+4模乘. 通过转变坐标系(射影坐标系/雅可比坐标系等), 消除过程中的模逆运算
- *优化基础模运算*: 模逆运算采用 扩展欧几里得算法/费马小定理, 模乘运算采用蒙哥马利模乘算法/快速约简公式优化.

# 1 优化标量乘 $[k]P$

### 快速模幂运算

将标量k看作二进制数处理, 复杂度约为$\mathbb{O}(\log(k))$

```python
def ecc_mul(k: int, P: Point)->int:
	'''Elliptic Curve Point Multiplication
	, power mod method'''
	ans = (0, 0)
	base = P
	while k != 0:
		if k & 1 != 0:
			ans = self.add(base, ans) 
		base = self.double(base)
		k >>= 1
	return ans
```

> 注意到新定义类型 `Point=NewType("Point", Tuple(int, int))`


## NAF快速幂
> NAF详见 [非邻接形式整数NAF](../../../代数/非邻接形式整数NAF.md)

使用NAF稀疏表示整数, 可以加速快速模幂的过程, 同样的方法可以应用于ECC的点数乘之中.

一般整数k表示中, 非零位1的数量大概是$\frac{m}{2}$ (m是k的比特长度, 即$m\approx \log(k)$), 所以算法使用的操作数为 $\frac{m}{2}*A+m*D$ (其中A是点加操作, D是点倍乘操作)

在NAF整数k表示中, 非零位数量约等于$\frac{m}{3}$, 所以操作数为 $\frac{m}{3}*A+m*D$, 减少了更费时的点加操作.



# 2 优化模运算

## 模乘


## 模逆
费马小定理
欧几里得算法

# 3 转换坐标系
> to be continue...



## 参考

> [Elliptic curve point multiplication - Wikipedia](https://en.wikipedia.org/wiki/Elliptic_curve_point_multiplication#Point_doubling) 



