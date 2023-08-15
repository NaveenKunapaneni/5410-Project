import json
import boto3

ENDPOINT = 'https://1cw5xmuen5.execute-api.us-east-1.amazonaws.com/pythonProd/'
print(ENDPOINT)
client = boto3.client('apigatewaymanagementapi', endpoint_url=ENDPOINT)

names = {}

# Function to send a message to a particular team with teamID
def sendMessage(teamID, message):
    global names  # Add this line to access the global 'names' dictionary

    # Iterate through all user data and send the message to each user in the team
    for user_data in names.values():
        connection_id = user_data.get('connectionId')
        user_team_id = user_data.get('teamID')  # Assuming you have the teamID associated with the user_data
        if user_team_id == teamID and connection_id:
            user_name = user_data.get('name')
            data = (message)
            # Retrieve the key-value pair
            key = next(iter(data.keys()))
            value = data[key]
            try:
                client.post_to_connection(
                    ConnectionId=connection_id,
                    Data=json.dumps({key: f"{value}"}).encode('utf-8')
                )
            except Exception as e:
                print(e)

def lambda_handler(event, context):
    global names  # Add this line to access the global 'names' dictionary

    if 'requestContext' in event:
        connection_id = event['requestContext']['connectionId']
        route_key = event['requestContext']['routeKey']

        body = {}
        if 'body' in event:
            try:
                body = json.loads(event['body'])
            except json.JSONDecodeError as e:
                print(e)

        if route_key == '$connect':
            pass
        elif route_key == '$disconnect':
            # when any user disconnects from the socket, send this message
            user_data = names.get(connection_id)
            
            if user_data:
                user_name = user_data['name']
                message = {"System": f"{user_name} has left the chat"}
                sendMessage(user_data.get('teamID'), message)
                del names[connection_id]
                sendMessage(list(names.keys()), {'members': list(names.values())})
            pass
        elif route_key == 'default':
            pass
        elif route_key == 'setTeamName':
            print(body)
            team_id = body['teamID']
            user_name = body['name']
            names[connection_id] = {'connectionId': connection_id, 'name': user_name, 'teamID': team_id}
            print(names)
            message = {"System": f"{user_name} has joined the chat"}
            # when any user connects to the socket, send this message
            sendMessage(team_id, message)
            sendMessage(list(names.keys()), {'members': list(names.values())})
            pass
        elif route_key == 'sendMessage':
            team_id = body['teamID']
            print(team_id)
            user_name = body['name']
            message = body['message']
            # msg = {"from": user_name, "to": team_id, "message": message}
            # msg = {"message": message}
            # print(msg)
            user_data = names.get(connection_id)
            if user_data:
                user_name = user_data['name']
                msg = {user_name: message}
                # Call the updated sendMessage function with the teamID and message
                sendMessage(user_data.get('teamID'), msg)
        else:
            pass

    response = {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
    return response
