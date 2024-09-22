"""Test steps for adding a new match."""

from pytest_bdd import scenario, then, when
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import select, wait


@scenario("new_match.feature", "Add a new match to an existing season")
def test_new_match(
    authbrowser,
):
    """Auto-collect steps and test scenario."""


@scenario("new_match.feature", "Add a new fixed duration match to an existing season")
def test_new_timed_match(
    authbrowser,
):
    """Auto-collect steps and test scenario."""


@scenario("new_match.feature", "Cancel adding a new match")
def test_cancel_match(authbrowser):
    """Auto-collect steps and test scenario."""


@scenario("new_match.feature", "Season only shows up for admin")
def test_non_admin_list(nonadmin_authbrowser):
    """Auto-collect steps and test scenario."""


@scenario("new_match.feature", "Nonadmin unable to add new match")
def test_non_admin_no_add(nonadmin_authbrowser):
    """Auto-collect steps and test scenario."""


@when("I browse to the first season in the list")
def browse_to_seasons_list(
    season_name,
    authbrowser,
):
    """Click on the season link and ensure we got to the details page."""
    seasons = authbrowser.find_elements(By.TAG_NAME, "a")
    [s for s in seasons if s.text == season_name][0].click()
    wait.WebDriverWait(authbrowser, 3).until(
        lambda b: b.find_element(By.TAG_NAME, "h1").text == season_name
    )
    assert authbrowser.find_element(By.TAG_NAME, "h1").text == season_name


@when("I click to add a match")
def click_add_match(authbrowser):
    matches = authbrowser.find_elements(By.CSS_SELECTOR, ".match.row")
    assert ("Kento", "Victor") not in [
        (p.text for p in m.find_elements(By.CSS_SELECTOR, ".match-player")) for m in matches
    ]
    authbrowser.find_element(By.ID, "button-new-match").click()


@when("I enter valid data and submit")
def enter_valid_match_data(authbrowser):
    authbrowser.find_element(By.ID, "select2-id_first_player-container").click()
    authbrowser.find_element(By.CSS_SELECTOR, ".select2-search__field").send_keys(
        "Ken" + Keys.RETURN
    )
    authbrowser.find_element(By.ID, "select2-id_second_player-container").click()
    authbrowser.find_element(By.CSS_SELECTOR, ".select2-search__field").send_keys(
        "Vic" + Keys.RETURN
    )
    select.Select(authbrowser.find_element(By.NAME, "match_type")).select_by_visible_text("Sets")
    date_input = authbrowser.find_element(By.NAME, "date_played")
    date_input.clear()
    date_input.send_keys("1.3.2020")
    authbrowser.find_element(By.NAME, "first_score_1").send_keys(21)
    authbrowser.find_element(By.NAME, "second_score_1").send_keys(19)
    authbrowser.find_element(By.NAME, "first_score_2").send_keys(21)
    authbrowser.find_element(By.NAME, "second_score_2").send_keys(11)
    authbrowser.find_element(By.NAME, "submit").click()


@when("I enter valid data for a fixed duration match and submit")
def enter_valid_timed_match_data(authbrowser):
    authbrowser.find_element(By.ID, "select2-id_first_player-container").click()
    authbrowser.find_element(By.CSS_SELECTOR, ".select2-search__field").send_keys(
        "Vic" + Keys.RETURN
    )
    authbrowser.find_element(By.ID, "select2-id_second_player-container").click()
    authbrowser.find_element(By.CSS_SELECTOR, ".select2-search__field").send_keys(
        "Ken" + Keys.RETURN
    )
    select.Select(authbrowser.find_element(By.NAME, "match_type")).select_by_visible_text("Time")
    authbrowser.find_element(By.NAME, "minutes_played").send_keys("10")
    date_input = authbrowser.find_element(By.NAME, "date_played")
    date_input.clear()
    date_input.send_keys("1.4.2020")
    authbrowser.find_element(By.NAME, "first_score_1").send_keys(54)
    authbrowser.find_element(By.NAME, "second_score_1").send_keys(32)
    authbrowser.find_element(By.NAME, "submit").click()


@when("I click cancel")
def cancel_new_match(authbrowser):
    [e for e in authbrowser.find_elements(By.CLASS_NAME, "btn") if e.text == "Cancel"][0].click()


@then("The new match should be in the list")
def new_match_in_list(authbrowser):
    matches = authbrowser.find_elements(By.CSS_SELECTOR, ".match")
    new_match = None
    for match in matches:
        players = match.find_element(By.CSS_SELECTOR, ".match-players")
        if players.text == "Kento\nVictor":
            new_match = match
            break
    assert new_match
    scores = [i.text for i in new_match.find_elements(By.CSS_SELECTOR, ".match-score")]
    assert scores == ["21\n19", "21\n11"]


@then("The new fixed duration match should be in the list")
def new_timed_match_in_list(authbrowser):
    matches = authbrowser.find_elements(By.CSS_SELECTOR, ".match")
    new_match = None
    for match in matches:
        players = match.find_element(By.CSS_SELECTOR, ".match-players")
        if players.text == "Victor\nKento":
            new_match = match
            break
    assert new_match
    assert new_match.find_element(By.CSS_SELECTOR, ".match-duration").text == "10'"
    scores = [i.text for i in new_match.find_elements(By.CSS_SELECTOR, ".match-score")]
    assert scores == ["54\n32"]


@then("I should not see the add match button")
def no_add_match(nonadmin_authbrowser):
    assert not nonadmin_authbrowser.find_elements(By.ID, "button-new-match")
    assert not [
        link
        for link in nonadmin_authbrowser.find_elements(By.TAG_NAME, "a")
        if link.text == "New Match"
    ]


@then("I should not see any seasons")
def season_not_in_list(nonadmin_authbrowser, season_name):
    assert not [
        link
        for link in nonadmin_authbrowser.find_elements(By.TAG_NAME, "a")
        if link.text == season_name
    ]
