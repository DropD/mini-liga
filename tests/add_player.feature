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
