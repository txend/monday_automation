import requests
from itertools import groupby
import re

# DATA we need for the requests, this should not change.
# URL might change based on updates of the Monday API
# The key will change if it's regenerated or if this script is used with a different account
API_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjk0NTQyMDIzLCJ1aWQiOjE2MzAzNDExLCJpYWQiOiIyMDIwLTEyLTMxVDE0OjAyOjIyLjAwMFoiLCJwZXIiOiJtZTp3cml0ZSIsImFjdGlkIjo3MTgzMzI2LCJyZ24iOiJ1c2UxIn0._Zh50Nwc4gWQGWzGOgyTiJIhqGrz3rZj6Jw-oG1T5UM"
URL_ENDPOINT = "https://api.monday.com/v2"
HEADERS = {"Authorization": API_KEY, "Content-Type": "application/json"}


def check_event_inputs(column_type):
    is_event_status = False
    is_event_notes = False
    is_event_due_date = False
    # event_value = str(input_data['event_column_type'])
    event_value = column_type
    if event_value == "Notes":
        is_event_notes = True

    if event_value == "Due Date" or event_value == "Task Due Date":
        is_event_due_date = True

    if event_value == "Status":
        is_event_status = True

    return is_event_notes, is_event_due_date, is_event_status

def process_update_info(
    board_ids,
    to_client_board,
    task_data,
    event_value,
    is_event_notes,
    is_event_due_date,
    is_event_status,
    previous_board_id,
    previous_task_id,
):
    # For all the board IDs retrieved
    for board_id in board_ids:

        if to_client_board:

            task_id = retrieve_client_task_id(task_data)
            # update_task(board_id, task_id, event_value, is_event_notes, to_client_board)
        else:

            # origin_board_name = get_origin_board_name(task_data)
            # task_id = get_destination_task_id(
            #     board_id,
            #     origin_board_name,
            #     task_data,
            #     previous_board_id,
            #     previous_task_id,
            # )
            task_id = get_destination_task_id(
                board_id, previous_board_id, previous_task_id
            )

            # We retrieve the corresponding task to update matching names
        print(f"TASK ID: {task_id}")

        # We then update the task with the new data
        # update_task(board_id, task_id, task_notes, task_status, to_client_board)
        update_task(
            board_id,
            task_id,
            event_value,
            is_event_notes,
            is_event_due_date,
            is_event_status,
            to_client_board,
        )
    return


def make_request(data):
    """"Makes the HTTP requests, since we are using GraphQL, the endpoint is the same, all that changes
    if the body request

    """
    payload = requests.post(URL_ENDPOINT, json=data, headers=HEADERS)
    json_payload = payload.json()
    print(payload.status_code)

    return json_payload


def get_task_data(task_id):
    """"Retrieves the task data using its ID

    """
    task_query = (
        "{ items (ids: ["
        + str(task_id)
        + "]) { name column_values {id value text title} board { name}}}"
    )
    data = {"query": task_query}
    payload = make_request(data)

    return payload


def check_sync_type(task_data):
    """"Checks the communication way by looking for the priority column,
    Which should only exist within ops boards

    """
    for i in task_data["data"]["items"][0]["column_values"]:
        try:
            if i["title"] == "Priority":
                return True

        except:
            pass
    return False


def get_client_name(task_data):
    """"Retrieves the client name using the task data

    """
    for i in task_data["data"]["items"][0]["column_values"]:
        try:
            if i["title"] == "Client":

                client_name = i["value"]
                client_name = client_name.strip('"')

                return client_name
        except:
            pass


def get_board_from_client(client_name):
    """"Retrieves the board ID using the client name
    We use pagination to find the board, it has a limit of 10 pages, but can easily be increased
    Since there are 25 results per page, this will work up to 250 boards in the account

    Another limitation is that it cannot have two boards with the same board name

    """
    for page in range(1, 40):

        board_query = "{boards(page: " + str(page) + ") {name id}}"
        data = {"query": board_query}
        payload = make_request(data)
        # print(payload)

        for i in payload["data"]["boards"]:
            try:
                # print(f"{i['name']} : \n{client_name}\n")
                if i["name"] == client_name:

                    return i["id"]

            except:
                pass

    print()
    print(f"CLIENT BOARD NOT FOUND: {client_name}")


def retrieve_client_board_id(task_data):
    linked_board_url = [
        value["text"]
        for value in task_data["data"]["items"][0]["column_values"]
        if value["text"] and value["text"].startswith("http")
    ][0]
    board_tasks_ids = [
        int("".join(group))
        for key, group in groupby(iterable=linked_board_url, key=lambda e: e.isdigit())
        if key
    ]
    client_board_id = board_tasks_ids[0]
    return client_board_id


def retrieve_client_task_id(task_data):
    linked_board_url = [
        value["text"]
        for value in task_data["data"]["items"][0]["column_values"]
        if value["text"] and value["text"].startswith("http")
    ][0]
    board_tasks_ids = [
        int("".join(group))
        for key, group in groupby(iterable=linked_board_url, key=lambda e: e.isdigit())
        if key
    ]
    client_task_id = board_tasks_ids[1]
    return client_task_id


def retrieve_task_status(task_data):
    for value in task_data["data"]["items"][0]["column_values"]:
        if value["id"] == "status":
            task_status = value["text"]
            print(task_status)
            if task_status:
                return task_status
            else:
                task_status = ""
                return task_status


def retrieve_ops_task_notes(task_data):
    for value in task_data["data"]["items"][0]["column_values"]:
        if value["id"] == "text5":
            task_status = value["text"]
            print(task_status)
            if task_status:
                return task_status
            else:
                task_status = ""
                return task_status


def retrieve_ops_task_date(task_data):
    for value in task_data["data"]["items"][0]["column_values"]:
        if value["id"] == "date4":
            task_status = value["text"]
            print(task_status)
            if task_status:
                return task_status
            else:
                task_status = ""
                return task_status


def retrieve_maps_task_notes(task_data):
    for value in task_data["data"]["items"][0]["column_values"]:
        if value["id"] == "text":
            task_status = value["text"]
            print(task_status)
            if task_status:
                return task_status
            else:
                task_status = ""
                return task_status


def retrieve_maps_task_date(task_data):
    for value in task_data["data"]["items"][0]["column_values"]:
        if value["id"] == "date1":
            task_status = value["text"]
            print(task_status)
            if task_status:
                return task_status
            else:
                task_status = ""
                return task_status


def retrieve_task_id(board_id, task_data):
    """"Retrieve the task ID

    """
    task_query = "{boards(ids: [" + str(board_id) + "]) {items {id name}}}"
    data = {"query": task_query}
    payload = make_request(data)
    # print()
    # print(payload)

    task_name = task_data["data"]["items"][0]["name"]

    for i in payload["data"]["boards"][0]["items"]:
        try:
            # print(f"{i['name']} : \n{task_name}\n")
            if i["name"] == task_name:

                return i["id"]

        except:
            pass

    print()
    print(f"TASK NOT FOUND: {task_name}")


def get_ops_users(task_data):
    """"Retrieves the ops user names using the task data

    """
    for i in task_data["data"]["items"][0]["column_values"]:
        try:
            if i["id"] == "people":

                people_list = i["text"].split(", ")

                return people_list
        except:
            pass


def get_board_from_ops_user(user_name):
    """"Retrieves board ID from the ops user
    We use pagination to find the board, it has a limit of 10 pages, but can easily be increased
    Since there are 25 results per page, this will work up to 250 boards in the account

    Another limitation is that it cannot have two boards with the same first name in it

    """
    name_list = user_name.split(" ")
    first_name = name_list[0]
    boards_ids = []
    for page in range(1, 35):

        board_query = "{boards(page: " + str(page) + ") {name id}}"
        data = {"query": board_query}
        payload = make_request(data)
        # print()
        # print(payload)

        for i in payload["data"]["boards"]:
            try:
                # print(f"{i['name']} : \n{client_name}\n")
                if first_name in i["name"]:
                    print("good_id", i["id"])
                    boards_ids.append(i["id"])
                    # return i['id']
                else:
                    continue

            except:
                pass

    # print()
    # print(f"OPS BOARD NOT FOUND: {first_name}")

    return boards_ids


def update_task(
    board_id,
    task_id,
    event_value,
    is_event_notes,
    is_event_due_date,
    is_event_status,
    to_client_board,
):
    """"Updates the task using the data retrieved from Zapier

    """

    mapping_ops = {"Notes": "text5", "Status": "status", "Due Date": "date4"}
    mapping_clients = {"Notes": "text", "Status": "status", "Task Due Date": "date1"}

    if to_client_board:
        mapping = mapping_clients
    else:
        mapping = mapping_ops

    if is_event_notes:
        column_id = mapping["Notes"]
    elif is_event_due_date and to_client_board:
        column_id = mapping["Task Due Date"]
    elif is_event_due_date and to_client_board == False:
        column_id = mapping["Due Date"]
    elif is_event_status:
        column_id = mapping["Status"]
    else:
        pass

    task = (
        "mutation { change_simple_column_value (board_id: "
        + str(board_id)
        + ", item_id: "
        + str(task_id)
        + ', column_id: "'
        + str(column_id)
        + '", value: "'
        + str(event_value)
        + '") {id}}'
    )

    # task = 'mutation { change_simple_column_value (board_id: 2327289931, item_id: 2458215873, column_id: "status", value: "In Progress") {id}}'
    data = {"query": task}
    payload = make_request(data)
    print("this is payload", payload)
    #
    return


def get_destination_task_id(board_id, previous_board_id, previous_task_id):
    """"Retrieve the task ID

    """
    # task_id = None
    # task_name = task_data["data"]["items"][0]["name"]

    task_query = (
        "{boards(ids: ["
        + str(board_id)
        + "]) {items {id name column_values {title value}}}}"
    )
    data = {"query": task_query}
    payload = make_request(data)

    board_items = payload["data"]["boards"][0]["items"]

    for columns in board_items:

        for value in columns["column_values"]:
            try:
                if value["title"] == "Link to Item":
                    # print(value["value"])
                    all_ids = re.findall("[0-9]+", value["value"])
                    if (
                        str(previous_board_id) in all_ids
                        and str(previous_task_id) in all_ids
                    ):
                        task_id = columns["id"]
                        print("This is founded_ task id", task_id)
                        return task_id
            except:
                pass


def get_origin_board_name(task_data):
    origin_board_name = task_data["data"]["items"][0]["board"]["name"]

    return origin_board_name


def board_processing(boardId = None, pulseId = None, column_type = None):
    previous_task_id = pulseId
    previous_board_id = boardId

    is_event_notes, is_event_due_date, is_event_status = check_event_inputs(column_type)
    print(
        "MY TASK EXCEPT notes:",
        is_event_notes,
        type(is_event_notes),
        "DATA_EVENT",
        is_event_due_date,
        "STATUS_EVENT",
        is_event_status,
    )
    task_data = get_task_data(previous_task_id)

    # Check which way the communication needs to be done
    to_client_board = check_sync_type(task_data)

    board_ids = []

    # If the communication goes from the OPS board to the client board
    if to_client_board:

        print("FROM OPS TO CLIENT")

        # Retrieve the client name from the task
        # We will use it to find the board to send the changes to
        client_name = get_client_name(task_data)
        print("OPS CLIENT NAME:", client_name)

        client_board_id = retrieve_client_board_id(task_data)
        if is_event_notes:
            task_notes = retrieve_ops_task_notes(task_data)
            print("OPS CLIENT TASK NOTES:", task_notes)
            event_value = task_notes
        elif is_event_due_date:
            task_date = retrieve_ops_task_date(task_data)
            print("OPS CLIENT TASK DATE:", task_date)
            event_value = task_date
        elif is_event_status:
            task_status = retrieve_task_status(task_data)
            print("OPS CLIENT TASK STATUS:", task_status)
            event_value = task_status
        else:
            pass

        # Retrieve the ID of the board using the client name
        # previous_board_id = get_board_from_client(client_name)
        board_ids.append(client_board_id)

    # If the communication needs to go from the Client board to the OPS board(s)
    else:

        print("FROM CLIENT TO OPS")

        # From the task, retrieve the ops user names
        ops_user_names = get_ops_users(task_data)
        print("MAPS CLIENT NAME:", ops_user_names)

        # In case there are multiple users assigned to the task, we use a loop
        for user_name in ops_user_names:

            # Retrieve the board IDS using the ops user names
            board_ids.extend(get_board_from_ops_user(user_name))

        if is_event_notes:
            task_notes = retrieve_maps_task_notes(task_data)
            print("MAPS CLIENT TASK NOTES:", task_notes)
            event_value = task_notes
        elif is_event_due_date:
            task_date = retrieve_maps_task_date(task_data)
            print("MAPS CLIENT TASK DATE:", task_date)
            event_value = task_date
        elif is_event_status:
            task_status = retrieve_task_status(task_data)
            print("MAPS CLIENT TASK STATUS:", task_status)
            event_value = task_status
        else:
            pass

    print()
    print(f"BOARD IDS: {board_ids}")
    if is_event_notes:
        process_update_info(
            board_ids,
            to_client_board,
            task_data,
            event_value,
            is_event_notes,
            is_event_due_date,
            is_event_status,
            previous_board_id,
            previous_task_id,
        )
    elif is_event_due_date:
        process_update_info(
            board_ids,
            to_client_board,
            task_data,
            event_value,
            is_event_notes,
            is_event_due_date,
            is_event_status,
            previous_board_id,
            previous_task_id,
        )
    elif is_event_status:
        process_update_info(
            board_ids,
            to_client_board,
            task_data,
            event_value,
            is_event_notes,
            is_event_due_date,
            is_event_status,
            previous_board_id,
            previous_task_id,
        )
    else:
        print("nothing to update")