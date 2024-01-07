# pip install statbotics==2.0.1
# https://www.statbotics.io/api/python for documentation on functions
import statbotics

# the statbotics api is mostly accessed through use of an object of the class statbotics.main.Statbotics
# ^the api is very easy to interact with, you just need that object and you can run a bunch of functions from it.
# each function calls a different statbotics api function
# added sb_ in front of each of the function names

# sb should be statbotics.Statbotics()
def sb_get_team(team, sb=statbotics.Statbotics()):
    # team is an integer
    # returns a dictionary
    return sb.get_team(team)


def sb_get_teams(
    country=None,
    state=None,
    district=None,
    active=True,
    metric="team",
    ascending=None,
    limit=100,
    offset=0,
    fields=["all"],
    sb=statbotics.Statbotics(),
):
    # returns a list of dictonaries of team data
    # restricted by the arguments
    # country -> restrict by country (select to include)
    # state -> restrict by US state or Canada province
    # district -> 2 or 3 letter key district
    # active – Restrict to active teams (played most recent season)
    # metric – Order output by field (Ex: “-norm_epa”, “team”, etc). Default is “team”.
    # ascending – Order output ascending or descending. Default varies by metric. (boolean)
    # limit – Limits the output length to speed up queries. Max 10,000
    # offset – Skips the first (offset) items when returning
    # fields – List of fields to return. Default is [“all”]
    return sb.get_teams(country, state, district, active, metric, ascending, limit, offset, fields)


def sb_get_year(year, fields=["all"], sb=statbotics.Statbotics()):
    # returns a dictionary with the year, match prediction statistics, and RP prediction statistics
    return sb.get_year(year, fields)


def sb_get_years(
    metric="year", ascending=None, limit=100, offset=0, fields=["all"], sb=statbotics.Statbotics()
):
    # returns a list of dictionaries such as those which would be returned by sb_get_year
    return sb.get_years(metric, ascending, limit, offset, fields)


def sb_get_team_year(team, year, fields=["all"], sb=statbotics.Statbotics()):
    # returns team data for a specific year (in a dictionary)
    return sb.get_team_year(team, year, fields)


def sb_get_team_years(
    team=None,
    country=None,
    state=None,
    district=None,
    metric="team",
    ascending=None,
    limit=100,
    offset=0,
    fields=["all"],
    sb=statbotics.Statbotics(),
):
    # returns a list of dictionaries of multiple (team, year) pairs
    return sb.get_team_years(
        team, country, state, district, metric, ascending, limit, offset, fields
    )


def sb_get_event(event, fields=["all"], sb=statbotics.Statbotics()):
    # returns a dictionary with the event and EPA statistics
    # event -> event key in a string (e.g. "2019cur")
    # fields -> list of fields to return
    return sb.get_event(event, fields)


def sb_get_events(
    year=None,
    country=None,
    state=None,
    district=None,
    type=None,
    week=None,
    metric="year",
    ascending=None,
    limit=100,
    offset=0,
    fields=["all"],
    sb=statbotics.Statbotics(),
):
    # returns a list of dictionaries, each with a tea, event, and epa statistics
    # week ->week of play, usually between 0 and 8
    # type -> 0=regional,1=district,2=district champ, 3=champs, 4=einstein
    return sb.get_events(
        year, country, state, district, type, week, metric, ascending, limit, offset, fields
    )


def sb_get_team_event(team, event, fields=["all"], sb=statbotics.Statbotics()):
    # returns a dictionary with event and epa statistics
    return sb.get_team_event(team, event, fields)


def sb_get_team_events(
    team=None,
    year=None,
    event=None,
    country=None,
    state=None,
    district=None,
    type=None,
    week=None,
    metric="year",
    ascending=None,
    limit=100,
    offset=0,
    fields=["all"],
    sb=statbotics.Statbotics(),
):
    # returns a list of multiple dictionaries
    return sb.get_team_events(
        team,
        year,
        event,
        country,
        state,
        district,
        type,
        week,
        metric,
        ascending,
        limit,
        offset,
        fields,
    )


def sb_get_match(match, fields=["all"], sb=statbotics.Statbotics()):
    # returns a dictionary with math, score breakdowns, and predictions
    # match -> match key in string form e.g. “2019cur_qm1”
    return sb.get_match(match, fields)


def sb_get_matches(
    team=None,
    year=None,
    event=None,
    week=None,
    elims=None,
    metric="time",
    ascending=None,
    limit=100,
    offset=0,
    fields=["all"],
    sb=statbotics.Statbotics(),
):
    # returns a list of dictionaries
    # elims -> restrict to only elimination matches, default False
    return sb.get_matches(team, year, event, week, elims, metric, ascending, limit, offset, fields)


def sb_get_team_match(team, match, fields=["all"], sb=statbotics.Statbotics()):
    # returns a dictionary with the team, match, alliance, and EPA statistics
    return sb.get_team_match(team, match, fields)


def sb_get_team_matches(
    team=None,
    year=None,
    event=None,
    week=None,
    match=None,
    elims=None,
    metric="time",
    ascending=None,
    limit=100,
    offset=0,
    fields=["all"],
    sb=statbotics.Statbotics(),
):
    # returns a list of dictionaries, each dictionary including the team, match, alliance, and elo
    return sb.get_team_matches(
        team, year, event, week, match, elims, metric, ascending, limit, offset, fields
    )
