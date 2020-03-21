import tvm
from tvm import relay
from tvm.contrib import graph_runtime
from tvm.contrib.download import download_testdata
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import networkx as nx
from dgl import DGLGraph
from dgl.data import load_data
from dgl.nn.pytorch import GraphConv
from collections import namedtuple
import timeit

########################
# Load graph data

def load_dataset(dataset="cora"):
    args = namedtuple("args", ["dataset"])
    data = load_data(args(dataset))
    # Remove self-loops to avoid duplicate passing of a node's feature to itself
    g = data.graph
    g.remove_edges_from(nx.selfloop_edges(g))
    # Add self-loops
    g.add_edges_from(zip(g.nodes, g.nodes))

    return g, data

dataset = "cora"
g, data = load_dataset(dataset)
num_layers = 1
num_hidden = 16
infeat_dim = data.features.shape[1]
num_classes = data.num_labels
features = torch.FloatTensor(data.features)
dgl_g = DGLGraph(g)


########################
# Define GCN in DGL-PyTorch

class GCN(nn.Module):
    def __init__(self,
                 g,
                 n_infeat,
                 n_hidden,
                 n_classes,
                 n_layers,
                 activation):
        super(GCN, self).__init__()
        self.g = g
        self.layers = nn.ModuleList()
        self.layers.append(GraphConv(n_infeat, n_hidden, activation=activation))
        for i in range(n_layers - 1):
            self.layers.append(GraphConv(n_hidden, n_hidden, activation=activation))
        self.layers.append(GraphConv(n_hidden, n_classes))

    def forward(self, features):
        h = features
        for i, layer in enumerate(self.layers):
            h = layer(self.g, h)
        return h

torch_model = GCN(dgl_g,
                  infeat_dim,
                  num_hidden,
                  num_classes,
                  num_layers,
                  F.relu)

########################
# Load pretrained parameters

model_url = "https://homes.cs.washington.edu/~cyulin/media/gnn_model/gcn_%s.torch"%(dataset)
# OrderedDict(["layers.i.weight",tensor],["layers.i.bias",tensor])
model_path = download_testdata(model_url, "gcn_%s.pickle"%(dataset), module='gcn_model')
torch_model_state_dict = torch.load(model_path)
torch_model.load_state_dict(torch_model_state_dict)

########################
# Evaluate the DGL-Pytorch model

def test_dgl():
    torch_model.eval()
    with torch.no_grad():
        logits_torch = torch_model(features)
    return logits_torch

def evaluate(data, logits):
    test_mask = data.test_mask # the test set which isn't included in the training phase

    pred = logits.argmax(axis=1)
    acc = ((pred == data.labels) * test_mask).sum() / test_mask.sum()

    return acc

logits_torch = test_dgl()
print("Print the first five outputs from DGL-PyTorch execution\n", logits_torch[:5])

acc = evaluate(data, logits_torch.numpy())
print("Test accuracy of DGL results: {:.2%}".format(acc))

repeat_times = 5
dgl_runing_time = timeit.timeit(setup='from __main__ import test_dgl',
                               stmt='test_dgl()',
                               number=repeat_times)
print("DGL running time: {:.2f} ms".format(dgl_runing_time / repeat_times * 1000))

########################
# Define gcn in TVM Relay

def GraphConv(layer_name,
              input_dim,
              output_dim,
              adj,
              inputs,
              norm=None,
              bias=True,
              activation=None):

    if norm is not None:
        inputs = relay.multiply(inputs, norm)

    weight = relay.var(layer_name + ".weight", shape=(input_dim, output_dim))
    weight_t = relay.transpose(weight)
    dense = relay.nn.dense(weight_t, inputs)
    output = relay.nn.sparse_dense(dense, adj)
    output_t = relay.transpose(output)
    if norm is not None:
        output_t = relay.multiply(output_t, norm)
    if bias is True:
        _bias = relay.var(layer_name + ".bias", shape=(output_dim, 1))
        output_t = relay.nn.bias_add(output_t, _bias, axis=-1)
    if activation is not None:
        output_t = activation(output_t)
    return output_t

########################
# Load parameters

params = {}
params['infeats'] = data.features.astype('float32') # Only support float32 as feature for now

# Generate adjacency matrix
adjacency = nx.to_scipy_sparse_matrix(g)
params['g_data'] = adjacency.data.astype('float32')
params['indices'] = adjacency.indices.astype('int32')
params['indptr'] = adjacency.indptr.astype('int32')

# Normalization w.r.t. node degrees
degs = [g.in_degree[i] for i in range(g.number_of_nodes())]
params['norm'] = np.power(degs, -0.5).astype('float32')
params['norm'] = params['norm'].reshape((params['norm'].shape[0], 1))

# Load model parameters
for i in range(num_layers+1):
    params["layers.%d.weight"%(i)] = torch_model_state_dict["layers.%d.weight"%(i)].numpy()
    params["layers.%d.bias"%(i)] = torch_model_state_dict["layers.%d.bias"%(i)].numpy()

# Check shape of features and the validity of adjacency matrix
assert len(params['infeats'].shape) == 2
assert params['g_data'] is not None and params['indices'] is not None and params['indptr'] is not None
assert params['infeats'].shape[0] == params['indptr'].shape[0] - 1

# Define input features, norms, adjacency matrix in Relay
infeats = relay.var("infeats", shape=data.features.shape)
norm = relay.Constant(tvm.nd.array(params['norm']))
g_data = relay.Constant(tvm.nd.array(params['g_data']))
indices = relay.Constant(tvm.nd.array(params['indices']))
indptr = relay.Constant(tvm.nd.array(params['indptr']))

Adjacency = namedtuple('Adjacency', ['data', 'indices', 'indptr'])
adj = Adjacency(g_data, indices, indptr)

layers = []
layers.append(GraphConv(
    layer_name="layers.0",
    input_dim=infeat_dim,
    output_dim=num_hidden,
    adj=adj,
    inputs=infeats,
    norm=norm,
    activation=relay.nn.relu
))
layers.append(GraphConv(
    layer_name="layers.1",
    input_dim=num_hidden,
    output_dim=num_classes,
    adj=adj,
    inputs=layers[-1],
    norm=norm,
    activation=None
))

output = layers[-1]


########################
# Start to compile the GCN model

target = 'llvm' # Currently only support `llvm` as target

func = relay.Function(relay.analysis.free_vars(output), output)

# Build with Relay
with relay.build_config(opt_level=0): # Currently only support opt_level=0
    graph, lib, params = relay.build(func, target, params=params)

########################
# Evaluate the TVM model

# Generate graph runtime
ctx = tvm.context(target, 0)
m = graph_runtime.create(graph, lib, ctx)
m.set_input(**params)

m.run()
logits_tvm = m.get_output(0).asnumpy()
# Verify the results with the DGL model
tvm.testing.assert_allclose(logits_torch, logits_tvm, atol=1e-3)
print("Print the first five outputs from TVM execution\n", torch.FloatTensor(logits_tvm)[:5])

acc = evaluate(data, logits_tvm)
print("Test accuracy of TVM results: {:.2%}".format(acc))

ftimer = m.module.time_evaluator("run", ctx, number=1, repeat=repeat_times)
prof_res = np.array(ftimer().results) * 1000  # convert to millisecond
print("Mean inference time (std dev): %.2f ms (%.2f ms)" % 
    (np.mean(prof_res), np.std(prof_res)))