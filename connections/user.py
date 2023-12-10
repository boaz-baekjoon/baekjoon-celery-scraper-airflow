import json
import subprocess
import logging

def register_users():

    # Read users from the JSON file
    with open('users.json', 'r') as f:
        users = json.load(f)

    # Iterate over users and use the airflow CLI to create each one
    for user in users:
        cmd = [
            'airflow', 'users', 'create',
            '--username', user['username'],
            '--firstname', user['firstname'],
            '--lastname', user['lastname'],
            '--role', user['role_name'],
            '--email', user['email'],
            '--password', user['password']
        ]
        
        # Execute the command
        subprocess.run(cmd, check=True)

    logging.info("All users have been created!")
    
    
if __name__ == '__main__':
    register_users()
    print('All users have been created!')