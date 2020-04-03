import tvm
import tvm.relay as relay
import numpy as np

# Ref: https://tvm.apache.org/docs/dev/relay_pass_infra.html

# Create a simple Relay program
def example():
    shape = (1, 64, 54, 54)
    c_data = np.empty(shape).astype("float32")
    c = relay.const(c_data)
    weight = relay.var('weight', shape=(64, 64, 3, 3))
    x = relay.var("x", relay.TensorType((1, 64, 56, 56), "float32"))
    conv = relay.nn.conv2d(x, weight)
    y = relay.add(c, c)
    y = relay.multiply(y, relay.const(2, "float32"))
    y = relay.add(conv, y)
    z = relay.add(y, c)
    z1 = relay.add(y, c)
    z2 = relay.add(z, z1)
    return relay.Function([x, weight], z2)

func = example()

# Customize the optimization pipeline
seq = relay.transform.Sequential([
    relay.transform.PrintIR(show_meta_data=False),
    relay.transform.FoldConstant(),
    relay.transform.PrintIR(show_meta_data=False),
    # relay.transform.EliminateCommonSubexpr(),
    # relay.transform.PrintIR()
])

# Create a module to perform optimizations.
mod = relay.Module({"main": func})

# Users can disable any passes that they don't want to execute by providing
# a list, e.g. disabled_pass=["EliminateCommonSubexpr"].
with relay.build_config(opt_level=2):
    with tvm.target.create("llvm"):
        # Perform the optimizations.
        mod = seq(mod)