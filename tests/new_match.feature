Feature: New Match

  Scenario: Add a new match to an existing season
    Given I am logged in on the season list

    When I browse to the first season in the list
    And I click to add a match
    And I enter valid data and submit

    Then I should be redirected to the season detail page
    And The new match should be in the list
