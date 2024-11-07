from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from .config import load_config

config = load_config()

def replace_newlines_with_br(text):
    return text.replace('\n', '<br>')

def create_ado_ticket(ticket_data, project="SupportAI", work_item_type='Issue'):
    credentials = BasicAuthentication('', config['ADO_PAT'])
    connection = Connection(base_url = config['ADO_BASE_URL'], creds=credentials)
    
    wit_client = connection.clients.get_work_item_tracking_client()

    # Replace \n with <br> in the description
    ticket_data['description'] = replace_newlines_with_br(ticket_data['description'])

    new_work_item = [
        {
            "op": "add",
            "path": "/fields/System.Title",
            "value": ticket_data['title']
        },
        {
            "op": "add",
            "path": "/fields/System.Description",
            "value": ticket_data['description']
        },
        {
            'op': 'add',
            'path': '/fields/Microsoft.VSTS.Common.Priority',
            'value': ticket_data['priority']
        }
    ]
    
    created_work_item = wit_client.create_work_item(
        project = project,
        type = work_item_type,
        document = new_work_item
    )
    
    return created_work_item.id