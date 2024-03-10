from data_transfer import tba_communicator
import warnings
from io import StringIO
import json
import csv
import logging
from datetime import datetime
from datetime import date

log = logging.getLogger(__name__)
YEAR = str(date.today())[:4]

# dictionary for converting bad datapoint names into section titles for the csv file
name_conversions = {
    "event_info": "EVENT INFO",
    "alliances": "ALLIANCES",
    "insights": "INSIGHTS",
    "oprs": "OPRs",
    "predictions.match_prediction_stats": "MATCH PREDICTION STATS",
    "predictions.match_predictions.playoff": "MATCH PREDICTIONS (PLAYOFF)",
    "predictions.match_predictions.qual": "MATCH PREDICTIONS (QUAL)",
    "predictions.stat_mean_vars.playoff": "PREDICTED STAT MEANS, VARS (PLAYOFF)",
    "predictions.stat_mean_vars.qual": "PREDICTED STAT MEANS, VARS (QUAL)",
    "predictions.ranking_predictions": "PREDICTED RANKINGS",
    "rankings.extra_stats_info": "RANKING EXTRA STATS INFO",
    "rankings.rankings": "FINAL/CURRENT RANKINGS",
    "rankings.sort_order_info": "RANKING SORT ORDER INFO",
    "district_points.points": "DISTRICT POINTS (POINTS)",
    "district_points.tiebreakers": "DISTRICT POINTS (TIEBREAKERS)",
    "teams": "TEAMS",
    "matches": "MATCHES",
    "awards": "AWARDS",
}


def pull_comp_data(event_key, only_match_team_data=False):
    # pulls all tba event data for one event
    # event_key is the tba event key
    comp_data = {}
    # for every type of event info tba api has, make an api request and pull the data, putting it in a dictionary
    if not only_match_team_data:
        comp_data["event_info"] = tba_communicator.tba_request(f"event/{event_key}")
        comp_data["alliances"] = tba_communicator.tba_request(f"event/{event_key}/alliances")
        # alliances has a single nested dictionary mapped to the key "status", so we seperate it into a bunch of single datapoints
        for i in range(len(comp_data["alliances"])):
            status_data = comp_data["alliances"][i].pop("status")
            for status_point, val in status_data.items():
                if isinstance(val, dict):
                    for k, v in val.items():
                        comp_data["alliances"][i][f"status.{status_point}.{k}"] = v
                else:
                    comp_data["alliances"][i][f"status.{status_point}"] = val
        comp_data["insights"] = tba_communicator.tba_request(f"event/{event_key}/insights")
    comp_data["oprs"] = tba_communicator.tba_request(f"event/{event_key}/oprs")
    if not only_match_team_data:
        # seperating all predictions into seperate categories
        predictions = tba_communicator.tba_request(f"event/{event_key}/predictions")
        if predictions != None:
            comp_data["predictions.match_prediction_stats"] = predictions["match_prediction_stats"]
            # seperating match predictions into playoff and qual because we can't have three axes
            comp_data["predictions.match_predictions.playoff"] = predictions["match_predictions"][
                "playoff"
            ]
            comp_data["predictions.match_predictions.qual"] = predictions["match_predictions"][
                "qual"
            ]
            comp_data["predictions.stat_mean_vars.playoff"] = {}
            comp_data["predictions.stat_mean_vars.qual"] = {}
            # formatting stat_mean_vars so it displays data per team instead of per datapoint
            # ^ tba gives it to us like {mean: {datapoint: {team: data}, datapoint: {team: data}}, var: {datapoint: {team: data}, datapoint: {team: data}}}
            # ^ but its easier to use it if it's like {datapoint: {team: {mean: data, var: data}, team: {mean: data, var: data}}, d: {t: {m: d, v: d}}}
            for stat in predictions["stat_mean_vars"]["qual"].keys():
                comp_data["predictions.stat_mean_vars.qual"][stat] = {}
                if predictions["stat_mean_vars"]["playoff"] != {}:
                    comp_data["predictions.stat_mean_vars.playoff"][stat] = {}
                for team in predictions["stat_mean_vars"]["qual"][stat]["mean"].keys():
                    comp_data["predictions.stat_mean_vars.qual"][stat][team] = {
                        "mean": predictions["stat_mean_vars"]["qual"][stat]["mean"][team],
                        "var": predictions["stat_mean_vars"]["qual"][stat]["var"][team],
                    }
                    if predictions["stat_mean_vars"]["playoff"] != {}:
                        comp_data["predictions.stat_mean_vars.playoff"][stat][team] = {
                            "mean": predictions["stat_mean_vars"]["playoff"][stat]["mean"][team],
                            "var": predictions["stat_mean_vars"]["playoff"][stat]["var"][team],
                        }
            # ranking predictions is a list of lists of stuff like [[team, [predictions, predictions]], [t, [p, p]]] which sucks
            # this code reformats it to [{"team_key": frc1678, "predictions": [predictions, predictions]}]
            comp_data["predictions.ranking_predictions"] = []
            for team in predictions["ranking_predictions"]:
                comp_data["predictions.ranking_predictions"].append(
                    {"team_key": team[0], "predictions": team[1]}
                )
        # seperating different rankings datapoints
        rankings = tba_communicator.tba_request(f"event/{event_key}/rankings")
        # extra_stats info is just the name of what the extra_stats field in ranking.rankings represents
        comp_data["rankings.extra_stats_info"] = rankings["extra_stats_info"]
        comp_data["rankings.rankings"] = rankings["rankings"]
        # tba gives us the teams record like {"losses": 0, "ties": 0, "wins": 0} but this seperates it into three seperate datapoints just like with alliances data
        for i in range(len(comp_data["rankings.rankings"])):
            record = comp_data["rankings.rankings"][i].pop("record")
            for record_point, val in record.items():
                comp_data["rankings.rankings"][i][f"record.{record_point}"] = val
        comp_data["rankings.sort_order_info"] = rankings["sort_order_info"]
        # idek what district_points is but they asked for "everything"
        district_points = tba_communicator.tba_request(f"event/{event_key}/district_points")
        if district_points != None:
            comp_data["district_points.points"] = district_points["points"]
            comp_data["district_points.tiebreakers"] = district_points["tiebreakers"]
        else:
            comp_data["district_points.points"] = {}
            comp_data["district_points.tiebreakers"] = {}
    comp_data["teams"] = tba_communicator.tba_request(f"event/{event_key}/teams")
    comp_data["matches"] = tba_communicator.tba_request(f"event/{event_key}/matches")
    # matches has this field as a nested dict like {"alliances": {"blue": {datapoint: data}, "red": {datapoint: data}}} so just like with records this seperates it into a bunch of individual datapoints
    # score breakdown as well needs to be seperated
    for i in range(len(comp_data["matches"])):
        if "alliances" in comp_data["matches"][i].keys():
            alliance_data = comp_data["matches"][i].pop("alliances")
            for color, data in alliance_data.items():
                for j, z in data.items():
                    comp_data["matches"][i][f"alliances.{color}.{j}"] = z
        if "score_breakdown" in comp_data["matches"][i].keys():
            score_breakdown = comp_data["matches"][i].pop("score_breakdown")
            if score_breakdown != None:
                for color, a in score_breakdown.items():
                    for scoretype, b in a.items():
                        if isinstance(b, dict):
                            for c, d in b.items():
                                comp_data["matches"][i][
                                    f"score_breakdown.{color}.{scoretype}.{c}"
                                ] = d
                        else:
                            comp_data["matches"][i][f"score_breakdown.{color}.{scoretype}"] = b
    if not only_match_team_data:
        comp_data["awards"] = tba_communicator.tba_request(f"event/{event_key}/awards")
        # removing useless values such as who gave the award to the team so the recipients list looks nicer
        for i in range(len(comp_data["awards"])):
            for j in range(len(comp_data["awards"][i]["recipient_list"])):
                comp_data["awards"][i]["recipient_list"][j] = comp_data["awards"][i][
                    "recipient_list"
                ][j]["team_key"]
    return comp_data


def export_csv(key, file_name):
    # exports event data from tba into a csv file
    # pull competition data from tba
    full_comp_data = pull_comp_data(key)
    # needed for ensuring the leftmost column is correct
    special_indexes = {
        "alliances": "name",
        "rankings.extra_stats_info": "name",
        "rankings.rankings": "rank",
        "rankings.sort_order_info": "name",
        "teams": "team_number",
        "matches": "key",
        "awards": "name",
        "predictions.ranking_predictions": "team_key",
    }
    # clearing file before writing
    with open(file_name, "w") as csv_file:
        for datapoint, data in full_comp_data.items():
            # write sectiont title
            csv_file.write(name_conversions[datapoint] + "\n")
            # making sure empty data doesn't give an error
            if (
                data != {}
                and data != None
                and not (datapoint == "insights" and data["qual"] == None)
            ):
                # writing to file with csv, with seperate if statements for differently formatted datapoints
                # these datapoints are lists (e.g. teams) so we need to iterate through them differently than if they were just dicts
                if isinstance(data, list):
                    # every item in the list has the same keys, so we just take the keys of the first one for the field names
                    field_names = list(data[0].keys())
                    if datapoint in special_indexes.keys():
                        field_names.insert(
                            0, field_names.pop(field_names.index(special_indexes[datapoint]))
                        )
                    # use csv module to write data into file
                    csv_writer = csv.DictWriter(csv_file, fieldnames=field_names)
                    csv_writer.writeheader()
                    for i in data:
                        csv_writer.writerow(i)
                # this datapoint isn't nested, so we just write it as one row of data
                elif datapoint == "event_info":
                    field_names = list(data.keys())
                    field_names.insert(0, field_names.pop(field_names.index("address")))
                    # use csv module to write data into file
                    csv_writer = csv.DictWriter(csv_file, fieldnames=field_names)
                    csv_writer.writeheader()
                    csv_writer.writerow(data)
                else:
                    # these datapoints are organized in a {team/match: {datapoint: data}} manner but we want datapoint to be in the header, not the team
                    # except insights, which is {playoff: {datapoint: data}, qual: {datapoint: data}} but again, we want datapoint in the header, not playoff/qual
                    if datapoint in [
                        "predictions.match_prediction_stats",
                        "predictions.match_predictions.playoff",
                        "predictions.match_predictions.qual",
                        "district_points.points",
                        "district_points.tiebreakers",
                        "insights",
                    ]:
                        # use csv module to write data into file
                        field_names = [""] + list(data[list(data.keys())[0]].keys())
                        csv_writer = csv.DictWriter(csv_file, fieldnames=field_names)
                        csv_writer.writeheader()
                        for i in data.keys():
                            # manually writing in the leftmost column (usually team number) since its a key pointing to the actual team data, not a key-value pair inside the team's dictionary
                            csv_file.write(i)
                            csv_writer.writerow(data[i])
                    # the remaining datapoints are organized in a {calculation/datapoint: {team: value}} manner
                    else:
                        field_names = [""] + list(data.keys())
                        csv_writer = csv.DictWriter(csv_file, fieldnames=field_names)
                        csv_writer.writeheader()
                        # for each team, write the entire row of data
                        for i in data[field_names[1]].keys():
                            teamdata = {}
                            for j in data.keys():
                                teamdata[j] = data[j][i]
                            # manually writing in the leftmost column (usually team number) since its a key pointing to the actual team data, not a key-value pair inside the team's dictionary
                            csv_file.write(i)
                            csv_writer.writerow(teamdata)
            else:
                # empty datapoints get this
                csv_file.write("N/A\n")
    log.info(f"Successfully wrote to {file_name}")


def export_all_comps(file_name):
    """Pulls data from every completed competition so far this year, then writes team and match data in the csv file"""
    # pull ALL comp data from current year events
    all_events = tba_communicator.tba_request(f"events/{YEAR}/simple")
    all_event_data = {}
    present = datetime.now()
    num_events_done = 0
    for event in all_events:
        if (
            datetime(
                int(event["end_date"][:4]),
                int(event["end_date"][5:7]),
                int(event["end_date"][8:10]),
            )
            < present
        ):
            all_event_data[event["key"]] = pull_comp_data(event["key"], True)
        num_events_done += 1
        # loading bar so that you can tell that its actually working :)
        percent_done = int(num_events_done / len(all_events) * 100)
        loading_bar_string = "Pulling event data... ["
        for i in range(20):
            loading_bar_string += "_" if percent_done < 5 * (i + 1) else "-"
        loading_bar_string += f"] {percent_done}%"
        print(loading_bar_string, end="\r")

    print(f"Writing data to {file_name}...    ")
    with open(file_name, "w") as csv_file:
        # match data
        csv_file.write(f"ALL {YEAR} MATCH DATA\n")
        all_match_data = []
        for event, data in all_event_data.items():
            all_match_data += data["matches"]
        field_names = list(all_match_data[0].keys())
        field_names.insert(0, field_names.pop(field_names.index("event_key")))
        field_names.insert(0, field_names.pop(field_names.index("key")))
        # writing data to file
        csv_writer = csv.DictWriter(csv_file, fieldnames=field_names)
        csv_writer.writeheader()
        for i in all_match_data:
            csv_writer.writerow(i)
        # team data, currently only includes opr data
        csv_file.write(f"{YEAR} TEAM DATA\n")
        all_oprs_data = []
        for event, data in all_event_data.items():
            data["oprs"]["event_key"] = event
            all_oprs_data.append(data["oprs"])
        field_names = ["team_key"] + list(all_oprs_data[0].keys())
        field_names.insert(1, field_names.pop(field_names.index("event_key")))
        # writing data to file
        csv_writer = csv.DictWriter(csv_file, fieldnames=field_names)
        csv_writer.writeheader()
        for event in all_oprs_data:
            if "ccwms" in event.keys():
                for i in event[field_names[2]].keys():
                    teamdata = {}
                    for j in event.keys():
                        if j != "event_key":
                            teamdata[j] = event[j][i]
                    teamdata["event_key"] = event["event_key"]
                    csv_file.write(i)
                    csv_writer.writerow(teamdata)
    print(f"Successfully wrote to {file_name}")


if __name__ == "__main__":
    all_or_single_comp = (
        input(f"Would you like to export data (only team and match) for all {YEAR} comps? (y/N)")
        == "y"
    )
    if not all_or_single_comp:
        key = input("Enter a tba event key: ")
        export_csv(key, f"data/tba_data_{key}.csv")
    else:
        export_all_comps("data/tba_data_2024_comps.csv")
