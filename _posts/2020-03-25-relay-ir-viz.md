---
layout: post
title: TVM - Relay IR计算图可视化
tags: [dl, tvm]
---

本文主要介绍如何将Relay IR的计算图(computational graph)/数据流图(dataflow graph)进行可视化输出。

<!--more-->

参照[TVM #3259](https://github.com/apache/incubator-tvm/pull/3259/files#)的Pull Request，将下列代码复制到`python/tvm/relay/visualize.py`中，注意代码做了一定的适应性修改。

```python
from .expr_functor import ExprFunctor
from . import expr as _expr
import networkx as nx

class VisualizeExpr(ExprFunctor):
    def __init__(self):
        super().__init__()
        self.graph = nx.DiGraph()
        self.counter = 0

    def viz(self, expr):
        assert isinstance(expr, _expr.Function)
        for param in expr.params:
            self.visit(param)

        return self.visit(expr.body)

    def visit_constant(self, const): # overload this!
        pass

    def visit_var(self, var):
        name = var.name_hint
        self.graph.add_node(name)
        self.graph.nodes[name]['style'] = 'filled'
        self.graph.nodes[name]['fillcolor'] = 'mistyrose'
        return var.name_hint

    def visit_tuple_getitem(self, get_item):
        tuple = self.visit(get_item.tuple_value)
        # self.graph.nodes[tuple]
        index = get_item.index
        # import pdb; pdb.set_trace()
        return tuple

    def visit_call(self, call):
        parents = []
        for arg in call.args:
            parents.append(self.visit(arg))
        # assert isinstance(call.op, _expr.Op)
        name = "{}({})".format(call.op.name, self.counter)
        self.counter += 1
        self.graph.add_node(name)
        self.graph.nodes[name]['style'] = 'filled'
        self.graph.nodes[name]['fillcolor'] = 'turquoise'
        self.graph.nodes[name]['shape'] = 'diamond'
        edges = []
        for i, parent in enumerate(parents):
            edges.append((parent, name, { 'label': 'arg{}'.format(i) }))
        self.graph.add_edges_from(edges)
        return name

def visualize(expr,mydir="relay_ir.png"):
    viz_expr = VisualizeExpr()
    viz_expr.viz(expr)
    graph = viz_expr.graph
    dotg = nx.nx_pydot.to_pydot(graph)
    dotg.write_png(mydir)
```

注意传入的参数需要时一个`ExprFunctor`实例，因此[原文](https://github.com/apache/incubator-tvm/pull/3259/files#)给出的测试实例调用`relay.testing.renet.getworkload()`得到模型并输出对v0.6版本并不可行。

下面复用上次GCN的[例子]({% post_url 2020-03-21-tvm-gcn %})，来生成计算图。

```python
from tvm.relay.visualize import visualize
func = relay.Function(relay.analysis.free_vars(output), output)
visualize(func)
```

执行上述代码之前需要先安装pydot和graphviz

```bash
pip install pydot
apt-get install graphviz
```

最后会生成对应的`relay_ir.png`图片，如下。

![relay ir](/files/programs/relay_ir.png)

实际上`VisualizeExpr`就是一个计算图的遍历器（以`visit`对结点进行访问），因此只要**重载**对应的结点函数，就可以实现对应的功能。