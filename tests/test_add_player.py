"""Test adding a player to a season."""
from pytest_bdd import scenario, then, when  # noqa: I900  # dev requirement
from selenium.webdriver.common.keys import Keys  # noqa: I900  # dev requirement


@scenario("add_player.feature", "Add a new player to a season")
def test_new_player(
    user_is_seasonadmin,
    season,
    user,
    authbrowser,
    client,
    live_server,
    transactional_db,
):
    """Collect scenario steps."""


@scenario("add_player.feature", "Add an existing player to a season")
def test_existing_player(
    user_is_seasonadmin,
    season,
    external_player,
    user,
    authbrowser,
    client,
    live_server,
    transactional_db,
):
    """Collect scenario steps."""


@when("I click to add a player")
def click_add_player(authbrowser):
    breakpoint()
    authbrowser.find_by_css(".bi-person-plus").click()


@when("I enter the name of a new player and submit")
def type_new_name_submit(authbrowser, season):
    authbrowser.find_by_id("select2-id_name-container").first.click()
    search_field = authbrowser.find_by_css(".select2-search__field").first
    search_field.click()
    search_field.type("Toma" + Keys.RETURN)
    authbrowser.find_by_name("submit").first.click()


@when("I enter the name of an existing player and submit")
def type_existing_name_submit(authbrowser, season, external_player):
    authbrowser.select("name", external_player.name)
    authbrowser.find_by_name("submit").first.click()


@then("the new player should be listed")
def new_player_listed(authbrowser):
    assert authbrowser.find_by_text("Toma")


@then("the added existing player should be listed")
def added_player_listed(authbrowser):
    assert authbrowser.find_by_text("Christo")


@then("the ranking should be updated with the new player")
def new_player_ranked(authbrowser):
    assert authbrowser.find_by_text("3. Toma").first


@then("the ranking should be updated with the added existing player")
def added_player_ranked(authbrowser):
    assert authbrowser.find_by_text("3. Christo").first
