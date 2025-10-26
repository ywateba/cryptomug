from behave import given, when, then
from starlette import status


@given("a clean application state")
def step_impl(context):
    # The before_scenario hook in environment.py already handles this.
    # This step is for readability in the feature file.
    pass


@when('I create a provider with name "{name}" and url "{url}"')
def step_impl(context, name, url):
    response = context.client.post("/providers/", json={"name": name, "url": url})
    context.response = response


@then('the provider "{name}" should be created successfully')
def step_impl(context, name):
    assert context.response.status_code == status.HTTP_201_CREATED
    response_json = context.response.json()
    assert response_json["name"] == name


@then('the list of providers should contain the provider "{name}"')
def step_impl(context, name):
    response = context.client.get("/providers/")
    assert response.status_code == status.HTTP_200_OK
    provider_names = [p["name"] for p in response.json()]
    assert name in provider_names
