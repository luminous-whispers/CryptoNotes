**MAC (message authentication code)**, 消息认证码

## MAC

**定义: 消息认证码MAC是一种消息认证技术, 是指消息被一密钥控制的公开函数作用后产生的, 用作认证符的, 固定长度的数值. 也被称为密码校验和.**  

消息认证包括*消息完整性认证*以及*信源身份认证*. 防御伪装和篡改行为.  
$MAC=(C, M)$. M为输入消息, C为MAC函数, K为共享密钥, MAC为消息认证码. 使用时和原消息一起发送.

MAC **优势和特点**:  
- 普通消息摘要只能保证完整性, 而MAC还能认证消息来源
- [公私钥体系](../公钥密码/签名和加密.md)有**不可抵赖性**; 而MAC双方都有密钥, 都可以伪造消息. MAC计算速度更快, 但不适合大规模分发.
- MAC可以任意长

Mac **实现方式**:
- 基于[杂凑函数](杂凑函数综述.md), 比如 HMAC
- 基于分组密码, 比如 OMAC/CBC-MAC/PMAC
- 基于伪随函数

## HMAC

HMAC是一种基于杂凑算法的MAC实现方式. 是 Keyed-hashing for MAC 的简写.  
HMAC可以基于不同杂凑算法, 有`HMAC-MD5`, `HMAC-SHA1`, `HMAC-SHA256`

$HMAC=Hash((K^{+}\oplus opad)\mid\mid Hash((K^{+}\oplus ipad)\mid\mid Msg))$

其中 
- Hash: 杂凑算法, 比如（MD5, SHA-1, SHA-256） 
- B: 块字节的长度, 取B=64。 
- L: 杂凑算法结果字节长度 (L=16 for MD5, L=20 for SHA-1)。 
- K：共享密钥. 若`len(k)>B`, 则先执行`Hash(k)`; 若`len(k)<B`, 则填充`0x00`至B长, 变为$K^{+}$.
- Msg： 要认证的消息 
- opad：外部填充常量，是 0x5C 重复B次。和$K^{+}$异或后, 效果是将其一般比特取反  
- ipad： 内部填充常量，是0x36 重复B次。

> 加速方式: 预先计算 $f(IV, (K^{+}\oplus ipad))$ 和 $f(IV, (K^{+}\oplus opad))$ 两个值. 其中$f(cv, block)$是散列函数的迭代压缩函数, 计算出的两个值可以作为新的$IV'$. 缺点是增加了HMAC算法和哈希算法的耦合度.

### HMAC的应用

HMAC用于用户身份验证:

1. 客户端发出登录请求 (比如浏览器GET请求) 
2. 服务器返回一个随机值 $r$ ，并在会话中记录 $r$ 
3. 客户端使用 $r$ 和 *用户密码*, 计算$HMAC_{user}$, 提交给服务器
4. 服务器从数据库读取 *用户密码* 和 $r$, 计算$HMAC_{server}$. 
5. 比对 $HMAC_{server}\equiv HMAC_{user}$, 若结果一致则用户合法.

敌手截获*随机值*与*用户发送hmac*结果, 无法获得用户密码. 引入随机值, 仅在当前会话有效, 避免*重放*攻击.

### `HMAC-SHA1` python实现

```python
# define some type
Int32 = int # 32bit int
Word = Int32
Int512 = int
BitLength = int
ByteLength = int

# define hash function
hash_funct = sha1
digest_size = 20 # sha1

block_size = 64
opad = b'\x5c' * block_size 
ipad = b'\x36' * block_size 


def _xor(x: bytes, y: bytes)->bytes:
    return bytes(x^y for x, y in zip(x, y))

def hmac(k: bytes, msg: bytes)->bytes:
    '''
    input k: shared key
    input msg: msg to be authenticate
    '''
    # test length of k, then padding
    if len(k) > block_size:
        k = hash_funct(k)
    while len(k) != block_size:
        k += b'\x00'
    
    # inside hash
    inside = hash_funct(_xor(k, ipad) + msg)
    
    # outside hash
    outside = hash_funct(_xor(k, opad) + inside)

    return outside
```


## 参考
> [HMAC算法及其应用 - 知乎](https://zhuanlan.zhihu.com/p/136590049)