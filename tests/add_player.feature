Feature: Add Player

  Scenario: Add a new player to a season
    Given I am logged in on the season detail view
    And I am season admin for the test season

    When I click to add a player
    And I enter the name of a new player and submit

    Then I should be redirected to the season detail page
    And the ranking should be updated with the new player

  Scenario: Add an existing player to a season
    Given I am logged in on the season detail view
    And I am season admin for the test season

    When I click to add a player
    And I enter the name of an existing player and submit

    Then I should be redirected to the season detail page
    And the ranking should be updated with the added existing player

  Scenario: Try to add an existing player from inaccessible season
    Given I am logged in on the season detail view
    And Another season which I do not manage contains separate players

    When I click to add a player
    And I click the player name input

    Then No players from the other season should be suggested
