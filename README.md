# 彩虹表实验报告

## 概况

- 本文是一篇实验报告，主要记录了这几天以来我对彩虹表的思考和实践。
- 实验需要生成基于 SHA256 口令的彩虹表并测试其成功率，破解范围为 5~6 位大小写字母加上数字组合而成的口令。
- 本算法能够生成一种非常规的彩虹表，能够以较低的计算量生成成功率大于 99.9% 的彩虹表。

## 实验环境

- CPU：AMD EPYC™ Milan(2.55GHz/3.5GHz) (2.55GHz/3.5GHz)
- 核心数：32
- 内存：64GB
- 编程语言：Python

## 实验过程

为了让自己放弃在性能上进行优化的想法，我选择了 Python 进行实验。

首先需要设定一下彩虹表的 R(Reduce) 函数，这里我借用了 Base64 进行转换。简单地说，将 SHA256 处理后的结果进行 Base64 编码，然后删除 `/` 和 `+`（如果第一位为 `+` 则本次生成的口令长度为 5），然后取前 5/6 个字符作为口令。基于 SHA256 输出空间的随机性，可以保证不会出现字符不够用的情况。为了代码的运行效率，具体的代码实现可能跟上面描述的过程不一致，但目的都是确保口令等概率出现。

接着我对彩虹表进行了模拟分析。影响彩虹表成功率的因素主要是链的覆盖元素数，要想让链的覆盖元素尽可能多就需要更多的链，但随着链的长度的增加，有越来越多的链会在某一轮计算出相同的口令，这会导致链的后半段完全重复，降低了链的覆盖元素数。根据不精确的模拟计算，链长度为 8192 时不同结尾的可能数估计为 14401573，占口令空间的 0.025%。在实验中，我生成了 15 种不同长度的链，并保证相同长度的链的结尾不重复（该处使用 Bloom Filter 算法），越短的链数量越多（因为长度越短结尾可能性越多），从而使得链能覆盖到的元素尽可能地多，破解成功率大大提高。具体分配如下：

| Length | Total     |
| ------ | --------- |
| 8192   | 11263901  |
| 6143   | 15020233  |
| 4606   | 20028909  |
| 3459   | 26707572  |
| 2591   | 35612396  |
| 1941   | 47493807  |
| 1454   | 63344796  |
| 1089   | 84491261  |
| 816    | 112666860 |
| 611    | 150265466 |
| 457    | 200591073 |
| 342    | 267465587 |
| 255    | 357407168 |
| 190    | 477157810 |
| 141    | 638666967 |

## 实验结果

- 彩虹表大小：5.074GB
- 制作彩虹表所需时间：25h64min（使用 30 个核心进行多进程并行计算）
- 制作彩虹表所需内存：6.1GB
- 理论破解成功率：99.975%
- 实际破解成功率：99.988%（连续 50000 次随机测试结果）
- 单次破解平均耗时：2.0082s（使用 32 个核心进行多进程并行计算）
