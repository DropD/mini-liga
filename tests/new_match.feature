Feature: New Match

  Scenario: Add a new match to an existing season
    Given I am logged in on the season list
    And I am season admin for the test season

    When I browse to the first season in the list
    And I click to add a match
    And I enter valid data and submit

    Then I should be redirected to the season detail page
    And The new match should be in the list
    And The ranking should be updated

  Scenario: Add a new fixed duration match to an existing season
    Given I am logged in on the season list
    And I am season admin for the test season

    When I browse to the first season in the list
    And I click to add a match
    And I enter valid data for a fixed duration match and submit

    Then I should be redirected to the season detail page
    And The new fixed duration match should be in the list
    And The ranking should be updated

  Scenario: Cancel adding a new match
    Given I am logged in on the season list
    And I am season admin for the test season

    When I browse to the first season in the list
    And I click to add a match
    And I click cancel

    Then I should be redirected to the season detail page
    And The ranking should be unchanged

  Scenario: Season only shows up for admin
    Given I am logged in on the season list

    Then I should not see any seasons

  Scenario: Nonadmin unable to add new match
    Given I am logged in on the season detail view

    Then I should not see the add match button
