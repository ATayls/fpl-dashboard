import plotly.express as px
import plotly.graph_objects as go

import pandas as pd


def league_ranking(running_rank):
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


def manager_box_plot(manager_df):
    fig = px.box(manager_df[['team_name', 'points']], x="points", y="team_name",
                 orientation='h')
    fig.update_yaxes(type='category')
    return fig


def transfers_in_bar(ownership_df, gw):
    total_transfers = ownership_df.diff(axis=1).fillna(0.0)
    total_transfers = total_transfers[total_transfers[f'gw{gw}'] > 0].sort_values(by=f'gw{gw}')
    fig = go.Figure(go.Bar(
                    x=total_transfers[f'gw{gw}'],
                    y=total_transfers.index,
                    orientation='h'))
    fig.update_yaxes(type='category')
    return fig


def ownership_bar(ownership_df, gw):
    gw_ownership = ownership_df[ownership_df[f'gw{gw}'] > 0].sort_values(by=f'gw{gw}')
    fig = go.Figure(go.Bar(
                    x=gw_ownership[f'gw{gw}'],
                    y=gw_ownership.index,
                    orientation='h'))
    fig.update_yaxes(type='category')
    return fig


def captaincy_plot(manager_df, gw):
    prc_captain = manager_df[manager_df['gw'] == gw]['captain'].value_counts()
    prc_captain = prc_captain / prc_captain.sum() * 100
    fig = go.Figure(go.Bar(
                    x=prc_captain,
                    y=prc_captain.index,
                    orientation='h'))
    fig.update_yaxes(type='category')
    return fig


def create_ranking_df(manager_df):
    def id_to_name(m_id):
        return manager_df[manager_df['manager'] == m_id]['team_name'].iloc[0]
    # Get manager rankings
    running_rank = (manager_df[['manager', 'gw', 'total_points', 'team_name']].set_index('manager')
                    .pivot(columns='gw', values='total_points')
                    .rank(ascending=False, method='first'))
    gw_rank = (manager_df[['manager', 'gw', 'points']].set_index('manager')
               .pivot(columns='gw', values='points')
               .rank(ascending=False, method='first'))
    running_rank.index = running_rank.index.map(id_to_name)
    gw_rank.index = gw_rank.index.map(id_to_name)
    return running_rank, gw_rank

def ownership(manager_df, prc=True, include_subs=True):
    """
    From manager_df, calculate the element percentage ownership by week
    :param manager_df:
    :return: prc_ownership_df
    """
    prc_ownership_df = pd.DataFrame()
    for gw in manager_df['gw'].unique():
        # Create percentage ownership for gameweek
        if include_subs:
            gw_df = manager_df[manager_df['gw'] == gw].loc[:, 'P1':'S4']
        else:
            gw_df = manager_df[manager_df['gw'] == gw].loc[:, 'P1':'P11']
        gw_ownership = gw_df.stack().value_counts()
        if prc:
            gw_ownership = gw_ownership / len(gw_df) * 100
        gw_ownership.name = f"gw{gw}"
        # Merge into main output dataframe
        prc_ownership_df = prc_ownership_df.merge(gw_ownership, how='outer', left_index=True, right_index=True)
    # Fill na with 0 and rename index
    prc_ownership_df = prc_ownership_df.fillna(0.0)
    prc_ownership_df.index.name = "element"
    return prc_ownership_df


def create_graphs(manager_df, gw):
    running_rank, gw_rank = create_ranking_df(manager_df)
    own_df = ownership(manager_df)
    rank_fig = league_ranking(running_rank)
    box_fig = manager_box_plot(manager_df)
    own_fig = ownership_bar(own_df, gw)
    cap_fig = captaincy_plot(manager_df, gw)
    trans_in = transfers_in_bar(own_df, gw)
    return {'rank': rank_fig, 'points-box': box_fig, 'prc-own': own_fig, 'captains': cap_fig, 'trans-in': trans_in}
