import pytest
import json

# test login user , get token
@pytest.mark.asyncio
async def test_login(client, test_user):
    response = client.post("/login", data=test_user)
    assert response.status_code == 200
    token = response.json()["token"]
    assert token is not None
    return token

# test auth with token
@pytest.mark.asyncio
async def test_get_me(client, test_user):
    token = await test_login(client, test_user)
    response = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["username"] == "test"

# test create company
@pytest.mark.asyncio
async def test_create_company(client, test_user, test_company):
    token = await test_login(client, test_user)
    if isinstance(test_company, str):
        test_company = json.loads(test_company)
    
    response = client.post("/company/create", json=test_company, headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 200
    assert response.json()["name"] == "mycom"


# test sending invitation
@pytest.mark.asyncio
async def test_send_invitation(client, test_user):
    # Prepare test data
    token = await test_login(client, test_user)
    user_id = 49
    company_id = 29
 
    response = client.post(
        f"/action/invite/{user_id}?company_id={company_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Assert the response status code
    assert response.status_code == 200
    
    response_json = response.json()
    assert response_json["message"] == "Invitation sent succesfully."


# test cancel invitation
@pytest.mark.asyncio
async def test_cancel_invitation(client, test_user):
    # Prepare test data
    token = await test_login(client, test_user)
    invitation_id = 129
 
    response = client.delete(
        f"/action/cancel/{invitation_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    
    response_json = response.json()
    assert response_json["message"] == "Invitation canceled succesfully."

#test accept request
@pytest.mark.asyncio
async def test_accept_request(client, test_user):
    # Prepare test data
    token = await test_login(client, test_user)
    request_id = 28
 
    response = client.post(
        f"/action/accept/{request_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    
    response_json = response.json()
    assert response_json["message"] == "Request accepted succesfully."


#test users in company
@pytest.mark.asyncio
async def test_accept_request(client, test_user):
    # Prepare test data
    token = await test_login(client, test_user)
    company_id = 29
    page = 1
 
    response = client.get(
        f"/action/users/{company_id}?page={page}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    
    response_json = response.json()
    assert response_json[0]["user"] == {
                                  "username": "ivan",
                                  "email": "oleksin.966@gmail.com",
                                  "password": "$2b$12$FcSL9P.sU9i8Lf/Y2sP.XO/PLDX8XGsBCDDYKyLmso6VJsvOUAZS2",
                                  "age": None,
                                  "description": None
                                }