import plotly.express as px
import plotly.graph_objects as go


def league_ranking(running_rank):
    # League rank plot
    fig = go.Figure()
    for row in running_rank.iterrows():
        fig.add_trace(go.Scatter(x=row[1].index.to_list(), y=row[1].astype(int).to_list(),
                                 mode='lines+markers',
                                 name=row[0]))
    fig.update_layout(xaxis_title='GameWeek', yaxis_title='League Rank', yaxis_autorange="reversed",
                      yaxis_dtick=1, xaxis_dtick=1)
    return fig


def create_ranking_df(manager_df):
    # Get manager rankings
    running_rank = (manager_df[['manager', 'gw', 'total_points']].set_index('manager')
                    .pivot(columns='gw', values='total_points')
                    .rank(ascending=False, method='first'))
    gw_rank = (manager_df[['manager', 'gw', 'points']].set_index('manager')
               .pivot(columns='gw', values='points')
               .rank(ascending=False, method='first'))
    return running_rank, gw_rank


def create_graphs(manager_df):
    running_rank, gw_rank = create_ranking_df(manager_df)
    rank_fig = league_ranking(running_rank)
    return {'rank': rank_fig}
