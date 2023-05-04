import pandas as pd
import json
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
passing_dict = json.load(open('player_passing_data.json'))
rows = []
for team in passing_dict.keys():
    for player in passing_dict[team].keys():
        for player_passed_to, num_passes in passing_dict[team][player].items():
            rows.append([player, player_passed_to, num_passes])


edge_data = pd.DataFrame(rows, columns = ['source_player', 'target_player', 'num_passes'])
edge_data['source_player'] = edge_data['source_player'].str.lower()
edge_data['target_player'] = edge_data['target_player'].str.lower()


per_poss_df = pd.read_csv('data/PerPossData.csv')
touches_df = pd.read_csv('data/TouchData.csv')
shooting_df = pd.read_csv('data/ShootingData.csv')

all_dfs = pd.merge(pd.merge(per_poss_df,shooting_df,on=['PLAYER', 'TEAM', 'AGE']),touches_df,on=['PLAYER', 'TEAM'])
all_dfs['PLAYER'] = all_dfs['PLAYER'].str.lower()
all_dfs['PLAYER'] = all_dfs['PLAYER'].str.replace(".", '')
all_dfs['PLAYER'] = all_dfs['PLAYER'].str.replace("'", '')
all_dfs['PLAYER'] = all_dfs['PLAYER'].str.replace('-', ' ')
node_data = all_dfs[all_dfs['PLAYER'].isin(set(list(edge_data['source_player'])))]
node_data.columns = node_data.columns.str.replace('\n', '_').str.replace(' ', '_').str.lower().str.replace('%', 'pct').str.replace('3', 'three_').str.replace('2', 'two_').str.replace('+', 'plus').str.replace('-', 'minus').str.replace('/', '_').str.replace('.', '')
node_data = node_data.loc[:, ~node_data.columns.str.contains('^unnamed')]
node_data = node_data.loc[:, ~node_data.columns.str.contains('^gp_')]
node_data = node_data.loc[:, ~node_data.columns.str.contains('^w_x')]
node_data = node_data.loc[:, ~node_data.columns.str.contains('^l_x')]
node_data = node_data.loc[:, ~node_data.columns.str.contains('^w_y')]
node_data = node_data.loc[:, ~node_data.columns.str.contains('^l_y')]
node_data = node_data.loc[:, ~node_data.columns.str.contains('^w_x')]
node_data = node_data.loc[:, ~node_data.columns.str.contains('^min_')]



node_data = node_data.loc[:, "player":].reset_index(drop=True)
node_data.to_csv('player_statistics.csv')
G = nx.DiGraph()

# add nodes with their attributes to the graph
for _, row in node_data.iterrows():
    node_attrs = {k: v for k, v in row.items() if k != 'player'}

    G.add_node(row['player'], **node_attrs)


# add edges with their weights to the graph
for _, row in edge_data.iterrows():
    if row['source_player'] in node_data['player'].unique() and row['target_player'] in node_data['player'].unique():
        teams_match = node_data[node_data['player']==row['source_player']]['team'].values[0]==node_data[node_data['player']==row['target_player']]['team'].values[0]
        if row['source_player'] in G.nodes and row['target_player'] in G.nodes and teams_match:
            weight=row['num_passes'] if row['num_passes']>0 else -1
            G.add_edge(row['source_player'], row['target_player'], weight=weight)




# nx.draw(G)
# plt.show()
nx.write_gml(G, "data/nba_network.gml")
nx.write_graphml_lxml(G, "data/nba_network.graphml")
