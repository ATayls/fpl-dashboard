import plotly.express as px
import plotly.graph_objects as go

from analysis import create_ranking_df, ownership, index_by_element, create_corr_matrices


def league_ranking(running_rank):
    """
    Plot to show manager overall rankings over time.
    :param running_rank: df
    :return: plotly fig
    """
    running_rank = running_rank.sort_values(by=running_rank.columns[-1], ascending=True)
    # League rank plot
    fig = go.Figure()
    for row in running_rank.iterrows():
        fig.add_trace(go.Scatter(x=row[1].index.to_list(), y=row[1].astype(int).to_list(),
                                 mode='lines+markers',
                                 name=row[0]))
    fig.update_layout(xaxis_title='GameWeek', yaxis_title='League Rank', yaxis_autorange="reversed",
                      yaxis_dtick=1, xaxis_dtick=1)
    return fig


def league_total_points(total_points):
    """
    Plot to show manager overall points over time.
    :param total_points: df
    :return: plotly fig
    """
    total_points = total_points.sort_values(by=total_points.columns[-1], ascending=True)
    # League rank plot
    fig = go.Figure()
    for row in total_points.iterrows():
        fig.add_trace(go.Scatter(x=row[1].index.to_list(), y=row[1].astype(int).to_list(),
                                 mode='lines+markers',
                                 name=row[0]))
    fig.update_layout(xaxis_title='GameWeek', yaxis_title='Total Points')
    return fig


def manager_box_plot(manager_df):
    """
    Plot to show manager points box plots.
    :param manager_df: df
    :return: plotly fig
    """
    fig = px.box(manager_df[['team_name', 'points']], x="points", y="team_name",
                 orientation='h')
    fig.update_yaxes(type='category')
    return fig


def transfers_bar(ownership_df, gw, in_out="in"):
    """
    Horizontal bar chart to show most transferred players. in_out param to select transfers in or transfers out.
    :param ownership_df:player ownership dataframe
    :param gw: gameweek
    :param in_out: transfer direction
    :return: plotly fig
    """
    total_transfers = ownership_df.diff(axis=1).fillna(0.0)
    if in_out == "in":
        total_transfers = total_transfers[total_transfers[f'gw{gw}'] > 0].sort_values(by=f'gw{gw}')
    elif in_out == "out":
        total_transfers = total_transfers[total_transfers[f'gw{gw}'] < 0].sort_values(by=f'gw{gw}')
        total_transfers = -1*total_transfers
    else:
        raise ValueError(f"{in_out} unrecognised")

    fig = go.Figure(go.Bar(
                    x=total_transfers[f'gw{gw}'],
                    y=total_transfers.index,
                    orientation='h'))
    fig.update_yaxes(type='category')
    return fig


def manager_corr_heatmap(manager_corr_matrix):
    """
    Heatmap of correlation between managers - which managers team selections are most correlated
    :param manager_corr_matrix: correlation matrix
    :return: plotly fig
    """
    fig = px.imshow(manager_corr_matrix.values,
                    labels=dict(x="Team Name", y="Team Name", color="Team Correlation"),
                    x=manager_corr_matrix.columns,
                    y=manager_corr_matrix.index
                    )
    return fig


def ownership_bar(ownership_df, gw):
    """
    Horizontal Bar chart plot of most owned players in league
    :param ownership_df: player ownership dataframe
    :param gw: input gameweek
    :return: plotly fig
    """
    gw_ownership = ownership_df[ownership_df[f'gw{gw}'] > 0].sort_values(by=f'gw{gw}')
    fig = go.Figure(go.Bar(
                    x=gw_ownership[f'gw{gw}'],
                    y=gw_ownership.index,
                    orientation='h'))
    fig.update_yaxes(type='category')
    return fig


def captaincy_plot(captains_df):
    """
    Horizontal Bar chart plot of most captained players in league
    :param captains_df:
    :return:
    """
    fig = go.Figure(go.Bar(
                    x=captains_df,
                    y=captains_df.index,
                    orientation='h'))
    fig.update_yaxes(type='category')
    return fig


def create_graphs(manager_df, players_df, gw):
    """
    Create all plotly fig objects and return in dictionary
    :param manager_df: Manager dataframe
    :param players_df: players dataframe
    :param gw: selected gameweek
    :return: dict
    """
    def id_to_name(player_id):
        return players_df[players_df['id'] == player_id]['web_name'].values[0]

    running_rank, gw_rank = create_ranking_df(manager_df)
    total_points, gw_points = create_ranking_df(manager_df, rank=False)
    own_df = ownership(manager_df)
    own_df.index = own_df.index.map(id_to_name)
    element_df = index_by_element(manager_df)
    element_df = element_df.rename(columns={x: id_to_name(x) for x in element_df.columns[3:]})
    player_corr, manager_corr = create_corr_matrices(element_df, gw)
    captains_df = manager_df[manager_df['gw'] == gw]['captain'].apply(id_to_name).value_counts()
    captains_df = captains_df / captains_df.sum() * 100

    rank_fig = league_ranking(running_rank)
    tpoints_fig = league_total_points(total_points)
    box_fig = manager_box_plot(manager_df)
    own_fig = ownership_bar(own_df, gw)
    cap_fig = captaincy_plot(captains_df)
    trans_in = transfers_bar(own_df, gw, "in")
    trans_out = transfers_bar(own_df, gw, "out")
    man_corr_fig = manager_corr_heatmap(manager_corr)

    return {'rank': rank_fig, 'points-box': box_fig, 'prc-own': own_fig, 'captains': cap_fig,
            'trans-in': trans_in, 'trans-out': trans_out, 'man-corr': man_corr_fig, 'total_points':tpoints_fig}
