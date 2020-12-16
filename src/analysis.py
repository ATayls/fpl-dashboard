import pandas as pd


def ownership(manager_df, prc=True, include_subs=True):
    """
    From manager_df, calculate the element percentage ownership by week
    :param include_subs:
    :param prc:
    :param manager_df:
    :return: prc_ownership_df
    """
    prc_ownership_df = pd.DataFrame()
    for gw in manager_df['gw'].unique():
        # Create percentage ownership for game week
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


def create_corr_matrices(element_df, gw):
    """
    Given the manager team selection df indexed by element, create correlation matrices for both player selection
    correlation and manager correlation
     i.e which players are often selected alongside others, and which managers teams are most correlated.
    :param element_df:
    :param gw:
    :return:
    """
    gw_element_df = element_df[element_df['gw'] == gw].drop(columns='gw').drop(columns='manager')
    gw_element_df = gw_element_df.loc[:, (gw_element_df.sum(axis=0) != 0)].set_index('team_name')
    player_corr_matrix = gw_element_df.corr()
    manager_corr_matrix = gw_element_df.transpose().corr()
    return player_corr_matrix, manager_corr_matrix


def index_by_element(manager_df, include_subs=True):
    """
    Transform main dataframe to be indexed by element
    :param include_subs:
    :param manager_df:
    :return:
    """
    if include_subs:
        element_df = manager_df.loc[:, 'P1':'S4'].apply(pd.value_counts, axis=1).fillna(0.0)
    else:
        element_df = manager_df.loc[:, 'P1':'P11'].apply(pd.value_counts, axis=1).fillna(0.0)
    element_df = pd.concat([manager_df[['manager', 'team_name', 'gw']], element_df], axis=1)
    return element_df


def create_ranking_df(manager_df, column, rank=True):
    """
    Create ranking dataframes given the manager dataframe and a specific column of interest.
    One of overall rank and one for rank in each gameweek.
    If rank is false return raw values.
    :param manager_df:
    :return:
    """
    def id_to_name(m_id):
        return manager_df[manager_df['manager'] == m_id]['team_name'].iloc[0]

    # Get manager rankings
    running_rank = (manager_df[['manager', 'gw', column, 'team_name']].set_index('manager')
                    .pivot(columns='gw', values=column))
    if rank:
        running_rank = running_rank.rank(ascending=False, method='first')
    running_rank.index = running_rank.index.map(id_to_name)
    return running_rank
