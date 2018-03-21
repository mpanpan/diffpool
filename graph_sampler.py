import networkx as nx
import numpy as np
import torch
import torch.utils.data

class GraphSampler(torch.utils.data.Dataset):
    ''' Sample graphs and nodes in graph
    '''
    def __init__(self, G_list, features='default'):
        self.adj_all = []
        self.len_all = []
        self.feature_all = []
        self.label_all = []

        self.max_num_nodes = max([G.number_of_nodes() for G in G_list])

        if features == 'default':
            self.feat_dim = G_list[0].node[0]['feat'].shape[0]
            print('Feat dim: ', self.feat_dim)

        for G in G_list:
            self.adj_all.append(nx.to_numpy_matrix(G))
            self.len_all.append(G.number_of_nodes())
            self.label_all.append(G.graph['label'])
            if features == 'default':
                f = np.zeros((self.max_num_nodes, self.feat_dim))
                for i,u in enumerate(G.nodes()):
                    f[i,:] = G.node[u]['feat']
                self.feature_all.append(f)
            elif features == 'id':
                self.feature_all.append(np.identity(max_num_nodes))
            elif features == 'deg':
                degs = np.sum(np.array(adj), 1)
                degs = np.expand_dims(np.pad(degs, [0, max_num_nodes - G.number_of_nodes()], 0),
                                      axis=1)
                self.feature_all.append(degs)
            elif features == 'struct':
                degs = np.sum(np.array(adj), 1)
                degs = np.expand_dims(np.pad(degs, [0, max_num_nodes - G.number_of_nodes()],
                                             'constant'),
                                      axis=1)
                clusterings = np.array(list(nx.clustering(G).values()))
                clusterings = np.expand_dims(np.pad(clusterings, 
                                                    [0, max_num_nodes - G.number_of_nodes()],
                                                    'constant'),
                                             axis=1)
                self.feature_all.append(np.hstack([degs, clusterings]))

    def __len__(self):
        return len(self.adj_all)

    def __getitem__(self, idx):
        adj = self.adj_all[idx]
        num_nodes = adj.shape[0]
        adj_padded = np.zeros((self.max_num_nodes, self.max_num_nodes))
        adj_padded[:num_nodes, :num_nodes] = adj

        # use all nodes for aggregation (baseline)

        return {'adj':adj_padded,
                'feats':self.feature_all[idx].copy(),
                'label':self.label_all[idx]}
