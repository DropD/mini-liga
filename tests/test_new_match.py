"""Test steps for adding a new match."""
from pytest_bdd import given, scenario, then, when  # noqa: I900 # dev requirements


@scenario("new_match.feature", "Add a new match to an existing season")
def test_new_match(
    season,
    user,
    user_is_seasonadmin,
    authbrowser,
    client,
    live_server,
    transactional_db,
    django_db_serialized_rollback,
):
    """Auto-collect steps and test scenario."""
    ...


@scenario("new_match.feature", "Cancel adding a new match")
def test_cancel_match(
    season,
    user,
    user_is_seasonadmin,
    authbrowser,
    client,
    live_server,
    transactional_db,
    django_db_serialized_rollback,
):
    """Auto-collect steps and test scenario."""
    ...


@given("I am logged in on the season list")
def logged_in(
    authbrowser,
    index_page,
):
    """Ensure logged in and on seasons list."""
    authbrowser.visit(index_page)
    assert authbrowser.find_by_text("Running Seasons")


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
    authbrowser.find_link_by_partial_text("new match").click()


@when("I enter valid data and submit")
def enter_valid_match_data(season, authbrowser):
    kento_pk = season.participants.get(name="Kento").pk
    victor_pk = season.participants.get(name="Victor").pk
    authbrowser.select("first_player", kento_pk)
    authbrowser.select("second_player", victor_pk)
    authbrowser.select("match_type", "Points")
    authbrowser.fill("date_played", "1.3.2020")
    authbrowser.fill("first_score_1", 21)
    authbrowser.fill("second_score_1", 19)
    authbrowser.find_by_name("submit").first.click()


@when("I click cancel")
def cancel_new_match(authbrowser):
    authbrowser.find_link_by_text("Cancel").click()


@then("I should be redirected to the season detail page")
def redirected_to_season(
    season_name,
    authbrowser,
):
    assert authbrowser.find_by_tag("h1").first.text == season_name


@then("The new match should be in the list")
def new_match_in_list(
    authbrowser,
):
    new_match = authbrowser.find_by_text("March 1, 2020").first
    assert new_match
    assert new_match.parent.find_by_text("Kento")
    assert new_match.parent.find_by_text("Victor")
    assert new_match.parent.find_by_text("21 : 19")
