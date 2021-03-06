Feature: Login

  Scenario: Try to access without logging in
    When I try to access the index page

    Then I should be asked to login

  Scenario: Login and access
    When I try to access the index page
    And I log in

    Then I should see the index page
