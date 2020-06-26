import tij_ranking as ranking
import numpy as np

# MA, Pj, %jamming required
weight = np.array([0.9, 0.5, 0.7])
threats = np.array([[0.4, 1.5, 0.5], [0.9, 0.5, 0.7], [0.5, 1.3, 0.5]])
p=10

normalizedThreats = ranking.normalizeThreat(threats, threats.shape)
for idx, threat in enumerate(normalizedThreats):
    rank = ranking.ranking(threat,p)
    rankWeigthed = ranking.rankingWeigthed(threat, weight, p)
    print("rank of threat {0}:\tnormal: {1}\tweighted: {2}\n".format(idx, rank, rankWeigthed))