"""Match - plan -> record workflow browser test steps."""
import bs4
from pytest_bdd import given, parsers, scenario, then, when
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


@scenario("plan_match_workflow.feature", "Plan matches")
def test_plan(authbrowser):
    """Collect scenario steps."""


@given("I am logged in on the planning feature season page")
def on_season_detail(authbrowser, index_page):
    """Visit the season detail page as season admin."""
    authbrowser.get(index_page + "/season/2")


@when(parsers.parse("I plan a match between {player_1} and {player_2}"))
def plan_a_match(authbrowser, player_1, player_2):
    """Click the 'Plan Match' button and enter two players and a date."""
    authbrowser.find_element(By.ID, "button-plan-match").click()
    authbrowser.find_element(By.ID, "select2-id_first_player-container").click()
    authbrowser.find_element(By.CSS_SELECTOR, ".select2-search__field").send_keys(
        player_1 + Keys.RETURN
    )
    authbrowser.find_element(By.ID, "select2-id_second_player-container").click()
    authbrowser.find_element(By.CSS_SELECTOR, ".select2-search__field").send_keys(
        player_2 + Keys.RETURN
    )
    date_input = authbrowser.find_element(By.NAME, "date_planned")
    date_input.clear()
    date_input.send_keys("10.5.2022")
    authbrowser.find_element(By.NAME, "submit").click()


@then(
    parsers.parse(
        "I should see the match between {player_1} and {player_2} in the planned matches list"
    )
)
def planned_match_shown(authbrowser, player_1, player_2):
    """Check that the entered match is in the planned matches list."""
    soup = bs4.BeautifulSoup(authbrowser.page_source, features="html.parser")
    section = soup.find(string="Planned Matches").parent.parent
    planned_list = [
        item
        for item in section.find(attrs={"class": "matchlist"}).children
        if item and item != "\n"
    ]
    matches = planned_list[1:]
    planned_matches = [
        match.find(attrs={"class": "col"}).text.strip() for match in matches
    ]
    assert planned_list[0].text == "May 10, 2022"
    assert f"{player_1}\n{player_2}" in planned_matches


@scenario("plan_match_workflow.feature", "Record results")
def test_record():
    """Collect and run test steps."""


@given(parsers.parse("There is a planned match between {player_1} and {player_2}"))
def has_planned_match(authbrowser, index_page, player_1, player_2):
    """Check planned match is there."""
    authbrowser.get(index_page + "/season/2")
    soup = bs4.BeautifulSoup(authbrowser.page_source, features="html.parser")
    section = soup.find(string="Planned Matches").parent.parent
    planned_list = [
        item
        for item in section.find(attrs={"class": "matchlist"}).children
        if item and item != "\n"
    ]
    matches = planned_list[1:]
    planned_matches = [
        match.find(attrs={"class": "col"}).text.strip() for match in matches
    ]
    assert f"{player_1}\n{player_2}" in planned_matches


@when(
    parsers.parse(
        "I record the result for {player_1} and {player_2} as {p11} : {p21}, {p12} : {p22}"
    )
)
def record_result(authbrowser, player_1, player_2, p11, p21, p12, p22):
    """Record a result to the planned match."""
    record_link = [
        match
        for match in authbrowser.find_elements(By.CSS_SELECTOR, ".match.row")
        if match.text.strip() == f"{player_1}\n{player_2}"
    ][0]
    record_link.click()
    authbrowser.find_element(By.NAME, "first_score_1").send_keys(p11)
    authbrowser.find_element(By.NAME, "second_score_1").send_keys(p21)
    authbrowser.find_element(By.NAME, "first_score_2").send_keys(p12)
    authbrowser.find_element(By.NAME, "second_score_2").send_keys(p22)
    date_input = authbrowser.find_element(By.NAME, "date_played")
    date_input.clear()
    date_input.send_keys("11.5.2022")
    authbrowser.find_element(By.NAME, "submit").click()


@then(
    parsers.parse(
        "I should see the match between {player_1} and {player_2} with "
        "{p11} : {p21}, {p12} : {p22} in the played matches list"
    )
)
def match_in_played_list(authbrowser, player_1, player_2, p11, p21, p12, p22):
    """Check the recorded match result is in the latest played list and not in the planned list."""
    soup = bs4.BeautifulSoup(authbrowser.page_source, features="html.parser")
    if soup.find(string="Planned Matches"):
        plannedlist = soup.find(string="Planned Matches").parent.parent.find(
            attrs={"class": "matchlist"}
        )
        assert f"{player_1}\n{player_2}" not in [
            i.text.strip() for i in plannedlist.children if i != "\n"
        ]
    matchlist = soup.find(string="Latest Matches").parent.parent.find(
        attrs={"class": "matchlist"}
    )
    matches = []
    for item in matchlist:
        if item == "\n":
            continue
        matches.append(
            {
                "players": [
                    i.text.strip()
                    for i in item.find_all(attrs={"class": "match-player"})
                ],
                "scores": [
                    i.text for i in item.find_all(attrs={"class": "match-score"})
                ],
            }
        )
    reference = {
        "players": [player_1, player_2],
        "scores": [f"{p11}{p21}", f"{p12}{p22}"],
    }
    assert reference in matches
