import requests
import os
from argparse import ArgumentParser


class ConfigurationError(Exception):
    pass


def get_env_variable(key: str) -> str:
    try:
        return os.environ[key]
    except KeyError:
        raise ConfigurationError(f"Environment variable {key} not set.")


def calculate_total_estimation(jira_url: str, jira_auth: tuple, jql_query: str):
    fields_to_retrieve = 'timetracking'
    response = requests.get(f"{jira_url}/rest/api/2/search?jql={jql_query}&fields={fields_to_retrieve}", auth=jira_auth)

    if response.status_code != 200:
        raise ConnectionError(f"Error {response.status_code}: {response.text}")

    issues = response.json().get('issues', [])
    total_original_estimate_seconds = sum(
        issue['fields']['timetracking'].get('originalEstimateSeconds', 0)
        for issue in issues
        if 'timetracking' in issue['fields']
    )

    print(f"Total number of issues: {len(issues)}")
    print(f"Total Original Estimate: {total_original_estimate_seconds / 60 / 60 / 8:.2f} days")


def main():
    try:
        jira_url = get_env_variable("JIRA_URL")
        jira_auth = (get_env_variable("JIRA_USER"), get_env_variable("JIRA_TOKEN"))

        parser = ArgumentParser()
        parser.add_argument('-e', '--epic-issue', required=True)
        config = parser.parse_args()

        calculate_total_estimation(jira_url, jira_auth, f'"Epic Link" = {config.epic_issue}')

    except ConfigurationError as ce:
        print(f"Configuration Error: {ce}")
    except ConnectionError as con_err:
        print(con_err)


if __name__ == "__main__":
    main()
