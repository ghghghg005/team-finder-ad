def _filter_users(me, key, users):
    """Apply one of the four predefined variant-1 user filters.""" 
    if key == constants.FILTER_FAVORITE_OWNERS: 
        return users.filter(owned_projects__in=me.favorites.all()) 
    if key == constants.FILTER_PARTICIPATING_OWNERS: 
        return users.filter(owned_projects__in=me.participated_projects.all()) 
    if key == constants.FILTER_INTERESTED_IN_MINE: 
        return users.filter(favorites__owner=me) 
    if key == constants.FILTER_PARTICIPANTS_OF_MINE: 
        return users.filter(participated_projects__owner=me) 
    return users 