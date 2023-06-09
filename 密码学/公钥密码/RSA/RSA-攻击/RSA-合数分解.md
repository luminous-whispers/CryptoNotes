> 该方法说明了, 在已知私钥情况下, 可以高效==还原出最初RSA两个素数p和q==.  
> 同时, 也揭示了==RSA最本质的安全性原理==.

观察参数: $n = p\times q$

和欧拉函数: 

$\begin{split}\phi(n)\ &=\ \phi(p\times q)\\&=\phi(p)\times\phi(q)\\&=(p-1)\times (q-1)\\&=p\times q-q-p+1\end{split}$

, 有: $n-(p+q)+1=\phi(n)$ 

故由韦达定理知,  
p和q是方程 $x^2-(p+q)*x+pq=0$ 的两个解, 其中 $p*q=n$ , $p+q=n-\phi(n)+1$

又因为: $d\ \times\ e\ \equiv\ 1\pmod{\phi(n)}$ ,有: $d\ \times\ e\ -1 =\ k*\phi(n)$

**如果能从 $k*\phi(n)$ 求出 $\phi(n)$, 就能解出p和q**.  
因为 $n-\phi(n)=p+q-1$, p和q数量级相对于n和 $\phi(n)$ 较小, 所以可以近似为 $1\approx\frac{\phi(n)}{n}$. 因此 $k\approx \frac{d*e-1}{n}=\frac{k*\phi(n)}{n}$. k较小, 基本不会有误差. 

现代RSA中p和q在 $2^{512}$ 数量级, n在 $2^{1024}$ 以上. 如果该法结果偏小, 说明$\frac{k*(p+q)}{n}>1$, 由于d和e都是在有限域上计算的, 这个k不会很大. 

## RSA 安全性

在RSA体系中, 公钥 $(e, n)$ 公开, 私钥 $(d, n)$ 保密.  
已知 $(e, n)$, 保证RSA安全的, 其实是**保证敌手由n求不出 $\phi(n)$**. 而为保证敌手求不出 $\phi(n)$, 则须保证敌手**无法求出 $n$ 的分解 $p\times q$**.

如果敌手由n能求出 $\phi(n)$, 那么他就能由e求出私钥d, 因为 $d\times e\equiv 1\pmod{\phi(n)}$.

而 $\phi(n)=p*q-q-p+1$, $n=p*q$, 所以两者的差只有 $\phi(n)-n=1-(p+q)$. 设想如果p和q过小, 那么敌手就易从n遍历出 $\phi(n)$.
