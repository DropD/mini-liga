"""Test steps for adding a new match."""
from pytest_bdd import scenario, then, when  # noqa: I900  # dev requirements
from selenium.webdriver.common.keys import Keys  # noqa: I900  # dev requirements


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
    authbrowser.links.find_by_text(season_name).click()
    assert authbrowser.find_by_tag("h1").first.text == season_name


@when("I click to add a match")
def click_add_match(authbrowser):
    assert not authbrowser.find_by_text("Kento vs. Victor")
    authbrowser.find_by_id("button-new-match").click()


@when("I enter valid data and submit")
def enter_valid_match_data(authbrowser):
    authbrowser.find_by_id("select2-id_first_player-container").first.click()
    authbrowser.find_by_css(".select2-search__field").type("Ken" + Keys.RETURN)
    authbrowser.find_by_id("select2-id_second_player-container").first.click()
    authbrowser.find_by_css(".select2-search__field").type("Vic" + Keys.RETURN)
    authbrowser.select("match_type", "Points")
    authbrowser.fill("date_played", "1.3.2020")
    authbrowser.fill("first_score_1", 21)
    authbrowser.fill("second_score_1", 19)
    authbrowser.fill("first_score_2", 21)
    authbrowser.fill("second_score_2", 11)
    authbrowser.find_by_name("submit").first.click()


@when("I enter valid data for a fixed duration match and submit")
def enter_valid_timed_match_data(authbrowser):
    authbrowser.find_by_id("select2-id_first_player-container").first.click()
    authbrowser.find_by_css(".select2-search__field").type("Vic" + Keys.RETURN)
    authbrowser.find_by_id("select2-id_second_player-container").first.click()
    authbrowser.find_by_css(".select2-search__field").type("Ken" + Keys.RETURN)
    authbrowser.select("match_type", "Time")
    authbrowser.fill("minutes_played", "10")
    authbrowser.fill("date_played", "1.4.2020")
    authbrowser.fill("first_score_1", 54)
    authbrowser.fill("second_score_1", 32)
    authbrowser.find_by_name("submit").first.click()


@when("I click cancel")
def cancel_new_match(authbrowser):
    authbrowser.find_link_by_text("Cancel").click()


@then("The new match should be in the list")
def new_match_in_list(
    authbrowser,
):
    matches = authbrowser.find_by_css(".match")
    new_match = None
    for match in matches:
        players = match.find_by_css(".match-players")
        if players.text == "Kento\nVictor":
            new_match = match
            break
    assert new_match
    scores = [i.text for i in new_match.find_by_css(".match-score")]
    assert scores == ["21\n19", "21\n11"]


@then("The new fixed duration match should be in the list")
def new_timed_match_in_list(
    authbrowser,
):
    matches = authbrowser.find_by_css(".match")
    new_match = None
    for match in matches:
        players = match.find_by_css(".match-players")
        if players.text == "Victor\nKento":
            new_match = match
            break
    assert new_match
    assert new_match.find_by_css(".match-duration").first.text == "10'"
    scores = [i.text for i in new_match.find_by_css(".match-score")]
    assert scores == ["54\n32"]


@then("I should not see the add match button")
def no_add_match(nonadmin_authbrowser):
    assert not nonadmin_authbrowser.find_by_id("button-new-match")
    assert not nonadmin_authbrowser.find_link_by_text("New Match")


@then("I should not see any seasons")
def season_not_in_list(nonadmin_authbrowser, season_name):
    assert not nonadmin_authbrowser.links.find_by_text(season_name)
