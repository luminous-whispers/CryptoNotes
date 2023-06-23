```
				     +----------+------+--+-------+
                DB = |  lHash   |  PS  |01|   M   |
                     +----------+------+--+-------+
                                    |
          +----------+              |
          |   seed   |              |
          +----------+              |
                |                   |
                |-------> MGF ---> xor
                |                   |
                V                   |
               xor <----- MGF <-----|
                |                   |
                V                   V
       +----+------------+----------------------------+
 EM =  | 00 | maskedSeed |          maskedDB          |
       +----+------------+----------------------------+
```

DB: data block
lHash: hash of label
MGF: mask generation function
PS: padding string