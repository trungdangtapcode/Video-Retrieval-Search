import faiss

resource = [faiss.StandardGpuResources()]

import numpy as np
d = 64                           # dimension
nb = 1000000                      # database size
nq = 10000                       # nb of queries
np.random.seed(1234)             # make reproducible
xb = np.random.random((nb, d)).astype('float32')
xb[:, 0] += np.arange(nb) / 1000.
xq = np.random.random((nq, d)).astype('float32')
xq[:, 0] += np.arange(nq) / 1000.


index = faiss.IndexFlatL2(d) 

print(index.is_trained)
gindex = faiss.index_cpu_to_gpu_multiple_py(resource, index)
gindex.add(xb)
# gindex.add(xb)
print(index.ntotal)
k = 4                          # we want to see 4 nearest neighbors
D, I = index.search(xb[:5], k) # sanity check
print(I)

GD, GI = gindex.search(xb[:5], k)
print(GI)