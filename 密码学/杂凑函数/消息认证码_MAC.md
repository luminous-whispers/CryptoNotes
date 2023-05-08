**MAC (message authentication code)**, 消息认证码

## MAC
消息认证码对消息来源及消息本身真实性进行认证. 能够识别出伪装和篡改等攻击行为

MAC 将以下信息进行组合与**消息摘要**:
1. 发送者与接收者间共享密钥
2. 需认证信息

MAC **优势和特点**:  
- 普通消息摘要只能保证完整性, 而MAC还能认证消息来源
- [公私钥体系](../公钥密码/签名和加密.md)有**不可抵赖性**; 而MAC双方都有密钥, 都可以伪造消息. MAC计算速度更快, 但不适合大规模分发.

Mac **实现方式**:
- 基于[杂凑函数](杂凑函数综述.md), 比如 HMAC
- 基于分组密码, 比如 OMAC/CBC-MAC/PMAC

## HMAC

HMAC是一种基于杂凑算法的MAC实现方式. 是 Keyed-hashing for MAC 的简写.  
HMAC可以基于不同杂凑算法, 有`HMAC-MD5`, `HMAC-SHA1`, `HMAC-SHA256`

$HMAC=Hash((K^{+}\oplus opad)\mid\mid Hash((K^{+}\oplus ipad)\mid\mid Msg))$

其中 
- Hash: 杂凑算法, 比如（MD5, SHA-1, SHA-256） 
- B: 块字节的长度, 取B=64。 
- L: 杂凑算法结果字节长度 (L=16 for MD5, L=20 for SHA-1)。 
- K：共享密钥. 若`len(k)>B`, 则先执行`Hash(k)`; 若`len(k)<B`, 则填充`0x00`至B长.
- Msg： 要认证的消息 
- opad：外部填充常量，是 0x5C 重复B次。 
- ipad： 内部填充常量，是0x36 重复B次。

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