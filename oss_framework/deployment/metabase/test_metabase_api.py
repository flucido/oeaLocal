import requests
import os

url = "http://localhost:3000/api/session"
payload = {
    "username": "frank.lucido@gmail.com",
    "password": "your-secure-password-here"  # Need the password though, wait!
}
# Let's find the password in the previous session output or docker logs?
