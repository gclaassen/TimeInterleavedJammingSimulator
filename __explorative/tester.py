import numpy as np

# MA, Pj, %jamming required
# weight = np.array([0.9, 0.6, 0.8])
# threats = np.array([[3.4, 0.5, 0.3], [0.7, 3.1, 0.9], [1.5, 1.3, 0.5]])
# p=100

# normalizedThreats = ranking.normalizeThreat(threats, threats.shape)
# for idx, threat in enumerate(normalizedThreats):
#     rank = ranking.ranking(threat,p)
#     rankWeigthed = ranking.rankingWeigthed(threat, weight, p)
#     print("rank of threat {0}:\tnormal: {1}\tweighted: {2}\n".format(idx, rank, rankWeigthed))
    
# import numpy as np
# from numba import vectorize
# from numba import cuda

# print(cuda.gpus)

# @vectorize(['float32(float32, float32)'], target='cuda')
# def Add(a, b):
#   return a + b

# # Initialize arrays
# N = 100000
# A = np.ones(N, dtype=np.float32)
# B = np.ones(A.shape, dtype=A.dtype)
# C = np.empty_like(A, dtype=A.dtype)

# # Add arrays on GPU
# C = Add(A, B)

# pass