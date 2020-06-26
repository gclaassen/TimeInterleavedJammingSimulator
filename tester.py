import tij_ranking as ranking

# MA, Pj, %jamming required
weight = (0.5, 0.2, 0.3)
threats = [(0.4, 0.2, 0.7), (0.9, 0.5, 0.7), (0.5, 2.1, 0.3)]
p=10

for idx, threat in enumerate(threats):
    rank = ranking.ranking(threat,p)
    rankWeigthed = ranking.rankingWeigthed(threat, weight, p)
    print("rank of threat {0}: normal {1}, weighted {2}\n".format(idx,rank, rankWeigthed))