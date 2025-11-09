import pytest
from httpx import AsyncClient
from fastapi import status

# Mark all tests in this file as async
pytestmark = pytest.mark.asyncio

@pytest.fixture(scope="function")
async def setup_users(async_client: AsyncClient):
    """
    A helper fixture to create 3 users (alice, bob, charlie)
    before each test function that needs them.
    """
    # Create Alice
    alice_res = await async_client.post("/api/users", json={
        "username": "alice", "age": 30, "hobbies": ["coding", "music"]
    })
    assert alice_res.status_code == status.HTTP_201_CREATED
    alice = alice_res.json()
    
    # Create Bob
    bob_res = await async_client.post("/api/users", json={
        "username": "bob", "age": 28, "hobbies": ["coding", "hiking"]
    })
    assert bob_res.status_code == status.HTTP_201_CREATED
    bob = bob_res.json()
    
    # Create Charlie
    charlie_res = await async_client.post("/api/users", json={
        "username": "charlie", "age": 25, "hobbies": ["music", "sports"]
    })
    assert charlie_res.status_code == status.HTTP_201_CREATED
    charlie = charlie_res.json()
    
    return {"alice": alice, "bob": bob, "charlie": charlie}


async def test_popularity_score_logic(
    async_client: AsyncClient, 
    setup_users
):
    """
    Tests the popularity score calculation.
    Logic: 1 friend + (1 shared hobby * 0.5) = 1.5
    """
    alice_id = setup_users["alice"]["id"]
    bob_id = setup_users["bob"]["id"]

    # 1. Link Alice and Bob
    link_res = await async_client.post(
        f"/api/users/{alice_id}/link", 
        json={"friend_id": bob_id}
    )
    assert link_res.status_code == status.HTTP_200_OK
    
    # 2. Check Alice's score
    alice_res = await async_client.get(f"/api/users/{alice_id}")
    assert alice_res.status_code == status.HTTP_200_OK
    assert alice_res.json()["popularity_score"] == 1.5
    
    # 3. Check Bob's score
    bob_res = await async_client.get(f"/api/users/{bob_id}")
    assert bob_res.status_code == status.HTTP_200_OK
    assert bob_res.json()["popularity_score"] == 1.5


async def test_link_creation_rules(
    async_client: AsyncClient, 
    setup_users
):
    """
    Tests that a user cannot be linked to themself and
    a link cannot be created twice (conflict).
    """
    alice_id = setup_users["alice"]["id"]
    
    # 1. Test self-linking
    self_link_res = await async_client.post(
        f"/api/users/{alice_id}/link", 
        json={"friend_id": alice_id}
    )
    assert self_link_res.status_code == status.HTTP_400_BAD_REQUEST
    assert "with oneself" in self_link_res.json()["detail"]
    
    # 2. Test duplicate linking
    bob_id = setup_users["bob"]["id"]
    
    # First link (should work)
    link_res_1 = await async_client.post(
        f"/api/users/{alice_id}/link", 
        json={"friend_id": bob_id}
    )
    assert link_res_1.status_code == status.HTTP_200_OK

    # Second link (should fail)
    link_res_2 = await async_client.post(
        f"/api/users/{alice_id}/link", 
        json={"friend_id": bob_id}
    )
    assert link_res_2.status_code == status.HTTP_409_CONFLICT
    assert "already exists" in link_res_2.json()["detail"]
    
    # Third link (test inverted B -> A) (should fail)
    link_res_3 = await async_client.post(
        f"/api/users/{bob_id}/link", 
        json={"friend_id": alice_id}
    )
    assert link_res_3.status_code == status.HTTP_409_CONFLICT


async def test_prevent_delete_when_linked(
    async_client: AsyncClient, 
    setup_users
):
    """
    Tests that a user cannot be deleted while linked.
    """
    alice_id = setup_users["alice"]["id"]
    bob_id = setup_users["bob"]["id"]

    # 1. Link Alice and Bob
    await async_client.post(
        f"/api/users/{alice_id}/link", 
        json={"friend_id": bob_id}
    )
    
    # 2. Try to delete Alice (should fail)
    delete_alice_res = await async_client.delete(f"/api/users/{alice_id}")
    assert delete_alice_res.status_code == status.HTTP_409_CONFLICT
    assert "Unlink first" in delete_alice_res.json()["detail"]
    
    # 3. Try to delete Bob (should fail)
    delete_bob_res = await async_client.delete(f"/api/users/{bob_id}")
    assert delete_bob_res.status_code == status.HTTP_409_CONFLICT
    assert "Unlink first" in delete_bob_res.json()["detail"]
    
    # 4. Unlink them
    unlink_res = await async_client.delete(
        f"/api/users/{alice_id}/unlink", 
        json={"friend_id": bob_id}
    )
    assert unlink_res.status_code == status.HTTP_200_OK
    
    # 5. Try to delete Alice (should work now)
    delete_alice_res_2 = await async_client.delete(f"/api/users/{alice_id}")
    assert delete_alice_res_2.status_code == status.HTTP_200_OK
    
    # 6. Try to delete Bob (should work now)
    delete_bob_res_2 = await async_client.delete(f"/api/users/{bob_id}")
    assert delete_bob_res_2.status_code == status.HTTP_200_OK