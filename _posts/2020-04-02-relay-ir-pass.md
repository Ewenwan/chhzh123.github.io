---
layout: post
title: TVM - Relay IR Pass
tags: [dl, tvm]
---

本文介绍Relay IR Pass的构造。

<!--more-->

Relay IR Pass核心依然是在C++中实现，但提供了Python接口，方便上层直接调用并对计算流图进行变换优化。

Pass管理器在`include/tvm/relay/transform.h`中，里面包含所有Pass的声明，希望做到
* 管理调度不同的优化pass
* 收集需要的分析信息，并且保持它们是最新的
* 减少程序员实现新pass的麻烦

Python的接口函数声明在`python/tvm/relay/transform.py`中，在`python/tvm/relay/_transform.py`中通过FFI对C++函数进行调用，命名空间为`relay._transform`。

具体C++的实现则分为两个部分：
* 高层IR图变换，源码在`src/relay/pass`中，集中变换则是在`src/relay/backend/build_module.cc`中的`relay::Module Optimize`
* 后端代码的图变换，源码在`src/relay/backend/vm`中，集中变换在`python/tvm/build_module.py`中的`lower`函数

## Pass的构造
* PassInfo
    ```cpp
    class PassInfoNode : public RelayNode {
    std::string name;
    int opt_level;
    std::vector<std::string> required;
    };
    ```
* PassContext
    ```cpp
    class PassContextNode : public RelayNode {
    public:
    ErrorReporter err_reporter;
    int opt_level{2};
    int fallback_device{static_cast<int>(kDLCPU)};
    tvm::Array<tvm::Expr> required_pass;
    tvm::Array<tvm::Expr> disabled_pass;
    };

    class PassContext : public NodeRef {
    public:
    TVM_DLL static PassContext Create();
    TVM_DLL static PassContext Current();
    /* Other fields are omitted. */

    private:
    // The entry of a pass context scope.
    TVM_DLL void EnterWithScope();
    // The exit of a pass context scope.
    TVM_DLL void ExitWithScope();

    // Classes to get the Python `with` like syntax.
    friend class tvm::With<PassContext>;
    };

    struct RelayPassContextThreadLocalEntry {
    /*! \brief The default pass context. */
    PassContext default_context;
    /*! \brief The current pass context. */
    std::stack<PassContext> context_stack;
    RelayPassContextThreadLocalEntry() {
        default_context = PassContext(make_node<PassContextNode>());
    }
    };

    /*! \brief The thread-local store to hold the pass context. */
    typedef dmlc::ThreadLocalStore<RelayPassContextThreadLocalEntry>
        RelayPassContextThreadLocalStore;
    ```
* Pass Constructs：提供基类
    ```cpp
    class PassNode : RelayNode {
    virtual PassInfo Info() const = 0;
    virtual Module operator()(const IRModule& mod
                                const PassContext& pass_ctx) const = 0;
    };
    ```

也就是说，一个Pass一定是作用在特定context下的`IRModule`，所有Pass都设计成`Module`到`Module`的映射，完整Pass的定义在`src/relay/ir/transform.cc`和`src/ir/transform.cc`中。

### Module-Level
```cpp
class ModulePassNode : PassNode {
  PassInfo pass_info;
  runtime::TypedPackedFunc<Module(Module, PassContext)> pass_func;
  Module operator()(const Module& mod, const PassContext& pass_ctx) const final;
  // Other members/methods are omitted
};
```

### Function-Level
```cpp
class FunctionPassNode : PassNode {
  PassInfo pass_info;
  runtime::TypedPackedFunc<Function(Function, Module, PassContext)> pass_func;
  Module operator()(const Module& mod, const PassContext& pass_ctx) const final;
  bool SkipFunction(const Function& func) const;
  // Other members/methods are omitted...
};
```

### Sequential
类似于PyTorch中的`nn.Sequential`，顺序执行多个Pass
```cpp
class SequentialPassNode : PassNode {
  PassInfo pass_info;
  // Passes need to be executed.
  Array<Pass> passes;
  bool PassEnabled(const PassInfo& info) const;
  Module operator()(const Module& mod, const PassContext& pass_ctx) const final;
};
```

## 参考资料
* TVM内置Pass索引，<https://docs.tvm.ai/api/python/relay/transform.html>
* Relay Pass Infrastructure, <https://tvm.apache.org/docs/dev/relay_pass_infra.html>