"""Test adding a player to a season."""

from pytest_bdd import scenario, then, when  # noqa: I900  # dev requirement
from selenium.webdriver.common.by import By  # noqa: I900  # dev requirement
from selenium.webdriver.common.keys import Keys  # noqa: I900  # dev requirement


@scenario("add_player.feature", "Add a new player to a season")
def test_new_player(
    authbrowser,
):
    """Collect scenario steps."""


@scenario("add_player.feature", "Add an existing player to a season")
def test_existing_player(
    authbrowser,
):
    """Collect scenario steps."""


@scenario("add_player.feature", "Try to add an existing player from inaccessible season")
def test_no_crossadmin_suggestions(authbrowser, hidden_player_names):
    """Collect scenario steps."""


@scenario("add_player.feature", "Add an existing player who is in multiple accessible seasons")
def test_add_seasoned_player(authbrowser):
    """Collect scenario steps."""


@when("I click to add a player")
def click_add_player(authbrowser):
    authbrowser.find_element(By.ID, "button-add-player").click()


@when("I enter the name of a new player and submit")
def type_new_name_submit(authbrowser):
    authbrowser.find_element(By.ID, "select2-id_name-container").click()
    search_field = authbrowser.find_element(By.CSS_SELECTOR, ".select2-search__field")
    search_field.click()
    search_field.send_keys("Toma" + Keys.RETURN)
    authbrowser.find_element(By.NAME, "submit").click()


@when("I enter the name of an existing player and submit")
def type_existing_name_submit(authbrowser):
    authbrowser.find_element(By.ID, "select2-id_name-container").click()
    search_field = authbrowser.find_element(By.CSS_SELECTOR, ".select2-search__field")
    search_field.send_keys("Chris")
    options = authbrowser.find_elements(By.CSS_SELECTOR, ".select2-results__option")
    [o for o in options if o.text == "Christo"][0].click()
    authbrowser.find_element(By.NAME, "submit").click()


@when("I enter the name of the target player and submit")
def type_target_name_submit(authbrowser):
    authbrowser.find_element(By.ID, "select2-id_name-container").click()
    search_field = authbrowser.find_element(By.CSS_SELECTOR, ".select2-search__field")
    search_field.send_keys("Akane")
    options = authbrowser.find_elements(By.CSS_SELECTOR, ".select2-results__option")
    [o for o in options if o.text == "Akane"][0].click()
    authbrowser.find_element(By.NAME, "submit").click()


@when("I click the player name input")
def click_player_name_input(authbrowser):
    authbrowser.find_element(By.ID, "select2-id_name-container").click()


@then("the ranking should be updated with the new player")
def new_player_ranked(authbrowser):
    assert authbrowser.find_elements(By.CSS_SELECTOR, "#season-ranking li")[2].text == "3. Toma"


@then("the ranking should be updated with the added existing player")
def added_player_ranked(authbrowser):
    assert authbrowser.find_elements(By.CSS_SELECTOR, "#season-ranking li")[3].text == "4. Christo"


@then("the ranking should be updated with the added target player")
def target_player_ranked(authbrowser):
    assert authbrowser.find_elements(By.CSS_SELECTOR, "#season-ranking li")[4].text == "5. Akane"


@then("No players from the other season should be suggested")
def no_cross_admin_players(authbrowser, hidden_player_names):
    option_elements = authbrowser.find_elements(By.CSS_SELECTOR, ".select2-results__option")
    suggested_names = [o.text for o in option_elements]
    assert not set(hidden_player_names).issubset(set(suggested_names))
