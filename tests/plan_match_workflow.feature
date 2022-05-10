Feature: Plan and record Matches

  Scenario: Plan matches

    Given I am logged in on the planning feature season page
    When I plan a match between <player_1> and <player_2>
    Then I should see the match between <player_1> and <player_2> in the planned matches list

    Examples:
      | player_1 | player_2 |
      | Mark     | Lee      |
      | Steve    | Dan      |

  Scenario: Record results

    Given There is a planned match between <player_1> and <player_2>
    When I record the result for <player_1> and <player_2> as <p11> : <p21>, <p12> : <p22>
    Then I should see the match between <player_1> and <player_2> with <p11> : <p21>, <p12> : <p22> in the played matches list

    Examples:
      | player_1 | p11 | p12 | player_2 | p21 | p22 |
      | Mark     | 21  | 21  | Lee      | 14  | 17  |
      | Steve    | 13  | 11  | Dan      | 21  | 21  |
