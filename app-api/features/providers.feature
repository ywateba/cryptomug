Feature: Provider Management
  As an API user, I want to manage data providers.

  Scenario: Create and retrieve a data provider
    Given a clean application state
    When I create a provider with name "CoinGecko" and url "https://api.coingecko.com/api/v3"
    Then the provider "CoinGecko" should be created successfully
    And the list of providers should contain the provider "CoinGecko"
