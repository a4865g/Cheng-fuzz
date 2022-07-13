# Cheng-fuzz
Fuzzing with the generated argument and environment variable.
It is based on [Yuan-fuzz](https://github.com/zodf0055980/Yuan-fuzz) and [Qiling example](https://github.com/qilingframework/qiling/blob/1.2.4/examples/fuzzing/dlink_dir815/dir815_mips32el_linux.py). You can see more detail in it.

## Architecture
![](https://i.imgur.com/hJnph0j.png)
- White Area: Original AFL++
- Green Area: Pre-processing and Qiling harness

We based on the multi-argument fuzz testing method proposed by SQ-Fuzz and Yuan-Fuzz to generate the command-line arguments in the mutation stage of AFL++. The method can test the environment variables of the target, and we pass the information through forkserver and set it so that the overall performance can be compatible with that of the AFL++.

We perform complete fuzz testing with little performance penalty on MIPS architecture by integrating the environment variable and combinations of parameters with the Qiling framework.
## Usage

Install [libxml2](https://gitlab.gnome.org/GNOME/libxml2) / [Qiling v1.2.4](https://github.com/qilingframework/qiling/tree/1.2.4) / [Ghidra 10.1.1](https://github.com/NationalSecurityAgency/ghidra/tree/Ghidra_10.1.1_build) first.

Then, the same installation method as AFL++(v3.15a). (Of course, you should install some dependent packages)

Build it like this:
```
$ make distrib
```

---

The command line usage of Cheng-fuzz is similar to Yuan-fuzz.
```
# Compile the target program
$ export CC=~/Cheng-fuzz/afl-clang-fast
$ export CXX=~/Cheng-fuzz/afl-clang-fast++
$ export AFL_LLVM_INSTRUMENT=AFL
$ export AFL_USE_ASAN=1
$ ./configure --disable-shared
$ make

# Fuzzing
$ ./afl-fuzz -i [testcase_dir] -o [out_dir] -k [~/XML_PATH/parameters.xml] -m none -- [Target program]
```

---

If you want to use Qiling harness and Unicorn-mode:
```
$ ./afl-fuzz -i [testcase_dir] -o [out_dir] -m none -U -- python3 qiling_harness.py @@
```
Of course you need to make modest changes to qiling_harness.py and config/wufuzz.cfg.

## Basic xml Rule
Cheng-fuzz's xml rule is different from Yuan-fuzz. Here is a simple example.
```xml  
<root>
    <ARGUMENT>
        <MUST>false</MUST>
        <ELEMENT>rot</ELEMENT>
        <ELEMENT>flip</ELEMENT>
    </ARGUMENT>
    <ARGUMENT>
        <MUST>true</MUST>
        <ELEMENT>@@</ELEMENT>
    </ARGUMENT>
    <ARGUMENT>
        <MUST>false</MUST>
        <ELEMENT>-i 10</ELEMENT>
        <ELEMENT>-i 100</ELEMENT>
    </ARGUMENT>
    <ENVIRONMENT>
        <NAME>ENV1</NAME>
        <MUST>true</MUST>
        <ELEMENT>VALUE_1</ELEMENT>
        <ELEMENT>VALUE_2</ELEMENT>
    </ENVIRONMENT>
    <ENVIRONMENT>
        <NAME>ENV2</NAME>
        <MUST>false</MUST>
        <ELEMENT>VALUE2_1</ELEMENT>
    </ENVIRONMENT>
</root>
```

Difference:
![](https://i.imgur.com/WrwvstG.png)

## Bug Reported
### libsixel
1. https://github.com/libsixel/libsixel/issues/25 (CVE-2021-40656)
2. https://github.com/libsixel/libsixel/issues/27 (CVE-2021-41715)
3. https://github.com/saitoha/libsixel/issues/156 (CVE-2022-27044)
4. https://github.com/saitoha/libsixel/issues/157 (CVE-2022-27046)
### Bento4
1. https://github.com/axiomatic-systems/Bento4/issues/708 (CVE-2022-31282)
2. https://github.com/axiomatic-systems/Bento4/issues/702 (CVE-2022-31285)
3. https://github.com/axiomatic-systems/Bento4/issues/703 (CVE-2022-31287)
4. https://github.com/axiomatic-systems/Bento4/issues/704
5. https://github.com/axiomatic-systems/Bento4/issues/705
6. https://github.com/axiomatic-systems/Bento4/issues/706
7. https://github.com/axiomatic-systems/Bento4/issues/707
8. https://github.com/axiomatic-systems/Bento4/issues/709
## Thanks
Use [SQ-fuzz](https://github.com/TommyWu-fdgkhdkgh/SQ-Fuzz), [Yuan-fuzz](https://github.com/zodf0055980/Yuan-fuzz) and [AFLplusplus](https://github.com/AFLplusplus/AFLplusplus) to modify.

