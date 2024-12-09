import requests

SYNAPSE_DOCKER_NAME = "synapse"
BASE_URL = "http://localhost:8008"
FULL_URL = BASE_URL + "/_matrix/client/v3/"

def login_user(user, password) -> dict:
    """Log this user in and return their session."""
    def generate_login_body(user, password) -> dict:
        body = {
                "type": "m.login.password",
                "identifier": {
                    "type": "m.id.user",
                    "user": user
                },
                "password": password
                }
        return body
    response = requests.post(
        FULL_URL + "login",
        json = generate_login_body(user, password)
    )
    # logging.debug(response)
    assert response.ok, f"Login failed for user {user}. You might need to restart the container"
    return response.json()

def get_auth_header(user_session):
    return {"Authorization": f"Bearer {user_session["access_token"]}"}

def get_room_ids() -> list:
    response = requests.get(
        BASE_URL + "/_synapse/admin/v1/rooms",
        headers=get_auth_header(admin_session),
    )
    assert response.ok
    return [x["room_id"] for x in response.json()["rooms"]]

def delete_room(room_id: str):
    response = requests.delete(
        BASE_URL + "/_synapse/admin/v2/rooms/" + room_id,
        headers=get_auth_header(admin_session),
        json={
            "purge": True,
            "force_purge": True,
            "block": False
            }
        )
    assert response.ok

admin_session = login_user("admin", "admin")
print(get_room_ids())
[delete_room(room_id) for room_id in get_room_ids()]
print(get_room_ids())