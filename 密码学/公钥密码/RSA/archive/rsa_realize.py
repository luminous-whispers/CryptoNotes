'''module may used:
1. extended Gcd done
2. 求逆元（基于欧几里得）done
3. 快速抹蜜算法 done
4. 密钥生成函数 done 
5. 素性检测算法 done
6. 中国剩余定理 done
7. 加解密，签名函数 done'''
from distutils.log import error
from logging import root
from math import floor, sqrt
from matplotlib.pyplot import close
import numpy
from itertools import chain
import random

def Egcd(a, b):
    '''扩展欧几里得求最大公因子算法
    当然也可以采用递归写法，但是会丢失s，t等有用的数据'''
    #matrix calculation
    r, s, t = a, 1, 0
    r1, s1, t1 = b, 0, 1
    #gcd
    while r1 != 0:
        q = r // r1# q = floor(r / r1), //是整数除法，规避浮点数(floor参数）有长度上限问题. 理论上python整型长度无上限
        tmp1, tmp2, tmp3 = r - r1 * q, s - s1 * q, t - t1 * q
        r, s, t = r1, s1, t1
        r1, s1, t1 = tmp1, tmp2, tmp3
    gcd = r
    assert gcd > 0, "gcd error"
    assert s * a + t * b == gcd, "s*a+t*b==gcd error"
    return s, t, gcd

def FindInverse(a, p):
    '''欧几里得方法计算逆元'''
    b,_,gcd=Egcd(a, p)
    assert gcd==1, "error, p and a is not relative prime" 
    return b % p

#todo 该函数有问题， level2中超大整数抹蜜运算不正确。是溢出，还是遗漏可能性？
#平凡乘算法, 注意这里的exp指数只能是正整数，其他情况请考虑系统pow
def fast_power_mod(num, exp, mod):
    '''平方乘算法，exp只能是正整数'''
    if judge_if_prime(mod)==True:
        num_bin = list(bin(exp%(mod-1))[2:]) #目前还没写phi欧拉函数, 写了之后通过调用可以去掉这个if句
    else:
        num_bin = list(bin(exp)[2:])
    r = len(num_bin)
    c = 1
    for i in range(r, 0, -1): #chain(range(),range())， 注意range是左闭右开区间
        c = ((c %mod) **2) %mod
        if int(num_bin[r-i]) == 1:
            c = (c%mod * num%mod)%mod
    return c

def fast_power_mod2(num, exp, mod):
    '''平方乘算法：更接近c的写法，位运算'''
    ans = 1
    base = num
    while exp != 0:
        if exp & 1 != 0:
            ans = (base*ans)%mod
        base = (base*base)%mod
        exp >>=1
    return ans %mod

def next_prime(n):
    n = (n + 1) | 1
    #这里|是位运算，当最后一位为1（也就是n为2时，n+1为奇数；n为奇素数的时候，n+1为偶数，最后一位就需要补1）
    #简而言之， 就是把2这个特殊素数情况放到一起考虑了
    while not judge_if_prime(n):
        n += 2
    return n

def judge_if_prime(n): 
    '''素性检测：Miller-Rabin + 偶数排除'''
    if n==2:
        return True
    elif n%2==0 or n<=1 :
        return False
    test_num = [2, 325, 9375, 28178, 450775, 9780504, 1795265022]
    #只能保证2^64之内准确，更大错误率很高。因为n越大，素数越稀疏
    for i in range(len(test_num)): 
    #test 10 times, correct possibility is 10^(-60)
        a = test_num[i]
        # print('testNum a:%s'%(a))
        *b, gcd = Egcd(a, n)
        if 1!=gcd:
            #if 1<gcd<n, return 0
            return False 
        #n - 1 == 2^k * q
        q, k = n - 1, 0
        while q%2==1:
            q = q/2
            k = k+1
        a = a^q % n
        if a%n == 1:
            break
        for j in range(0, k-1, 1):
            if a%n==n-1:
                break
            a = (a*a) %n
    return True 
    
def judge_if_relatively_prime(list):
    '''判断是否互素'''
    for i in range(0, len(list)):
        for j in range(i+1, len(list)):
            *_, gcd = Egcd(list[i], list[j])
            if gcd!=1:
                return False
    return True
    
def chinese_remainder_theorem(eq):
    '''eq: nested list of (b, m), 中国剩余定理'''
    m = []
    m_inverse = []
    b = []
    for pair in eq:
        b.append(pair[0])
        m.append(pair[1])
    assert judge_if_relatively_prime(m)==True, "m not relatively prime"
    M = numpy.prod(m)
    sum = 0
    for i in len(m):
       sum+=(FindInverse(M/m[i-1], m[i-1])*(M/m[i-1])*b[i-1])%M
    return sum

def divide_N_into_prime_list(N):
    '''traverse num < sqrt(N) to judge if num can divide N
    just ignore 1'''
    divisor = []
    if N%2 ==0:
        divisor.append(2)
        N /= 2
    i = 3
    while i <= int(sqrt(N)):
        if N%i==0:
            divisor.append(i)
            N /= i
        i+=2    
    if len(divisor) == 0:
        divisor.append(N)
    return divisor    

'''
暂且不用吧
def reslove_power_mod_equation(e, c, N):
    # 解决高次方程x^e=c modN
    divisor = divide_N_into_prime_list(N) 
    assert len(divisor)<=2, "error, N is a composite with three more factor, disability"
    if len(divisor)==1:
        d, _, gcd = Egcd(e, N-1)#notice that N = divisor[0]
        assert gcd == 1, "e don't have the inverse of N(p-1)"
        return fast_power_mod(c, d, N)
    elif len(divisor)==2:
        d, _, gcd = Egcd(e, (divisor[0]-1)*(divisor[1]-1))
        assert gcd == 1, "e don't have the inverse of (p-1)(q-1)"
        return fast_power_mod(c, d, N)
    # more cases to be continue...
'''
def new_safe_prime(bin_length):
    '''获取一个指定二进制长度的素数'''
    rand = random.randint(2**(bin_length-1), 2**(bin_length)-1)
    while judge_if_prime(rand)==False : #! 为了速度，牺牲这部分安全性啦 or judge_if_prime((rand-1)/2)==False:
        #通过检验(p-1)/2， 来检验rand是否是安全素数，来增加分解N的困难性
        rand = next_prime(rand)  #原本是再重新随机选一个随机数，但发现这样效率太低太低， 不如就在随机数附近开始寻找
    return rand

def get_relatively_prime_num(num, length):
    '''选出和参数num互素的一个数'''
    rand = random.randint(2**(length-1), 2**(length)-1)
    while judge_if_relatively_prime([rand, num])!=True:
        rand = random.randint(2**(length-1), 2**(length)-1)
    return rand

#RSA body part:
from AITMCLAB.Crypto.Util.number import  getRandomNBitInteger
from AITMCLAB.libnum import s2n
import json

def RSA_initial(usr):
    '''RSA密钥生成函数'''
    # 生成p、q部分
    p = new_safe_prime(516)
    while 1:
        q = new_safe_prime(508) #通过位数不同（516+508==1024），和p拉开大小差距。
        _,_,gcd= Egcd(p-1, q-1)
        if gcd == 2:
            #检测p-1，q-1的最大公因子是否过大. 
            #? 虽然但是，由于选的是安全素数，所以这一步并不是必要的，因为这个if大概率满足
            break;
    N = p * q
    #利用文件操作，给不同人不同N，防止共模攻击
    public_path = "./rsa/public_key.json"
    try:
        with open(public_path, mode = 'r') as f_in:
            old_info = json.load(f_in)
    except json.decoder.JSONDecodeError:
        """文件如果空时会出错"""
        print("empty existed public keys file, continuing...")
        f_in.close()
    else:
        for dict in old_info.values():
            assert dict['mod'] != N, "error, existed N, try again" 
            #由于没有跳转功能，考虑能否用递归。。。
            '''
            RAS_initial(usr)
            return;
            '''
        f_in.close()
    #生成d、e部分    
    phi = (p - 1) * (q - 1)
    d = random.randint(max(p, q), phi-1) 
    while judge_if_prime(d)==False or judge_if_relatively_prime([d, phi//gcd])==False: #! 同样为了速度牺牲安全性：or judge_if_prime((d-1)/2)==False:
        # d比较重要先选d，d要大于p、q，并且接近phi，并且是安全素数。这样也同时保证了d足够大(大于N**0.25)
        d = next_prime(d)
    e = FindInverse(d, phi//gcd) 
    assert e!=1 and e!=2, "error, e is too small, try again"

    #将公钥写入公共文件保存，私钥单独保存在用户文件夹
    with open(public_path, mode = "w") as f_pub_out:
        #公钥要检验是否已经该人已经生成了一对密钥了，如果已经存在需要覆盖原本密钥。
        info = {'owner': usr, 'public_key':e, 'mod':N}
        print('public keys:{}'.format(info)) #mark
        if not 'old_info' in dir():
            json.dump({usr:info}, f_pub_out)
        else:  
            for existed_usr in old_info.keys():
                if (existed_usr == usr):
                    old_info[usr] = info        
                else :
                    old_info.update({usr: info})
            json.dump(old_info, f_pub_out); #f_pub_out.write('\n')
        f_pub_out.close()
    private_path = './rsa/{}/private_key.json'.format(usr)
    with open(private_path, mode = "w") as f_pri_out: #json文件不支持： newline="\n"
        # 私钥由于每人只允许生成一对，由于保存结构，会直接覆盖写
        info = {'owner': usr, 'private_key':d, 'q':q, 'p':p, 'mod':N}
        json.dump(info, f_pri_out); #f_pri_out.write('\n')
        print('private keys:{}'.format(info)) #mark
        f_pri_out.close()
    print("success!")

def Encryption(msg, to_who):
    with open("./rsa/public_key.json", "r") as f_in:
        try:
            public_keys = json.load(f_in)
        except json.decoder.JSONDecodeError:
            print("error, empty public key! where to find e?")
            return
        for public_key in public_keys.values():
            if public_key['owner'] == to_who:
                e, N = public_key['public_key'], public_key['mod']
        assert e in vars(), "error, no matched public_key_for: to_who"
        f_in.close()
    cipher = fast_power_mod(msg, e, N)
    assert msg != cipher, "error, coincidence equal" #防止e==log(kn+m)时, 密文明文相同
    return cipher

def Decryption(usr, cipher):
    private_path = './rsa/{}/private_key.json'.format(usr)
    with open(private_path, "r") as f_in:
        try:
            key = json.load(f_in)
        except json.decoder.JSONDecodeError:
            print("error, empty private key, where to find d?")
            return;
        d, N = key['private_key'], key['mod']
        assert key['usr']==usr, "error, wrong owner for private key"
        f_in.close()
    return pow(cipher, d, N)

def Decryption_accelerate_with_pq(c, usr):
    private_path = './rsa/{}/private_key.json'.format(usr)
    with open(private_path, "r") as f_in:
        try:
            key = json.load(f_in)
        except json.decoder.JSONDecodeError:
            print("error, empty public key, where to find d?")
            return
        d = key['private_key']#暂且不检验是否赋值成功啦
        q, p = key['q'], key['p']
        assert key['usr']==usr, "error, wrong owner for private key"
        f_in.close()
    eq = []
    eq.append( pow((c%p), (d%(p-1)), p), p )
    eq.append( pow((c%q), (d%(q-1)), q), q )
    return chinese_remainder_theorem(eq)

def signature(msg, usr):
    private_path = './rsa/{}/private_key.json'.format(usr)
    with open(private_path, "r") as f_in:
        try:
            key = json.load(f_in)
        except json.decoder.JSONDecodeError:
           print("error, empty private key, where to find d?") 
           return
        d, N = key['private_key'], key['mod']
        assert key['usr'] ==usr, "error, wrong woner for private key"
        f_in.close()
    return pow(msg, d, N)

def verification(msg, signature, sender):
    with open("./rsa/public_key.json", "r") as f_in:
        try:
            public_keys = json.load(f_in)
        except json.decoder.JSONDecodeError:
            print("error, empty public key")
            return
        for public_key in public_keys.values():
            if public_key['owner'] == sender:
                e, N = public_key['public_key'], public_key['mod']
        assert e in vars(), "error, no matched public_key_for: to_who"
        f_in.close()
    to_verify = pow(signature, e, N)
    return int(to_verify) == int(msg)

RSA_initial("yjw")


