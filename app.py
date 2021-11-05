# app.py
#
# Applicant notes
#
# Hello,
#
# This was a fun assignment!
#
# It has been a while since I did python web development, and I had never used
# Flask before or python's unittest, so about one hour was spent getting up and
# running with python3, reading docs and configuring the heroku deploy.
#
# When working to fulfill the two member ID requirements (both verifiable and
# unique), I initially tried to implement a cryptographically secure and WC3
# compliant verifier relying on an external library (linked below) but in the
# end there were library incompatibilities.
#
# As a result, this current version merely satisfies it's own simple arithmetic
# verification scheme. I ran out of time before I was able to implement a quick
# database to ensure uniqueness. This repository also doesn't include tests.
#
# While my strongest background is in Javascript and PHP, I am a quick learner
# and appreciated the opportunity to stretch a bit and attempt to satisfy the
# basics here.
#
# Thank you for your time,
# Oren

from flask import Flask, request, jsonify, make_response
#from flask_sqlalchemy import SQLAlchemy
#from marshmallow import fields
#from marshmallow_sqlalchemy import ModelSchema
from iso3166 import countries_by_alpha2
import sqlite3 as sql
import random
from math import sqrt

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = ''
#db = SQLAlchemy(app)


# Issue new member ID
#
# Current (idiosyncratic, insecure) simple arithmetic verification scheme:
#
# ID numbers are 10 digits composed by appending three random prime numbers:
#
#     [3-digit prime] + [3-digit prime] + [4-digit prime]
#
# Uniqueness is checked before new member IDs are issued (saved to DB)
#
# @TODO Use a robust, cryptographically secure claim verification scheme.
# Read more: https://www.w3.org/TR/vc-data-model/
# Example implementation (blockchain): https://github.com/docknetwork/verifiable-claims-engine
@app.route('/member_id/', methods=['POST'])
def issue_id():
    first_name = request.form.get("first_name", None)
    last_name = request.form.get("last_name", None)
    dob = request.form.get("dob", None)
    country = request.form.get("country", None)
    receipt = f"Received {first_name} {last_name} {dob} {country}"
    print(receipt)

    response = {}

    if not first_name or not last_name or not dob or not country:
        response["success"] = False
        response["message"] = "Example Payload: {\"first_name\": \"Jose\", \"last_name\": \"Vasconcelos\", \"dob\": \"01/01/1961\", \"country\": \"MX\"}"
    else:
        new_id = generate_id()
        response["success"] = True
        response["id"] = new_id
        response["message"] = receipt
        # @TODO Save new ID to database for later global uniqueness check

    return jsonify(response)

def generate_id():
    new_id = attempt_unique_verifiable_id()
    is_unique = check_unique_id()
    while not is_unique:
        new_id = attempt_unique_verifiable_id()
        is_unique = check_unique_id()
    return new_id

def attempt_unique_verifiable_id():
    return random_prime(100,999) * 10000000 + random_prime(100,999) * 10000 + random_prime(1000,9999)

def random_prime(min,max):
    primes = primes_in_range(min,max);
    n = random.choice(primes)
    return n

def primes_in_range(x,y):
    prime_list = []
    for n in range(x, y):
        isPrime = is_prime(n)
        if isPrime:
            prime_list.append(n)

    return prime_list

# Fast standalone prime check
# Source: https://stackoverflow.com/questions/15285534/isprime-function-for-python-language
def is_prime(n):
  if n == 2 or n == 3: return True
  if n < 2 or n%2 == 0: return False
  if n < 9: return True
  if n%3 == 0: return False
  r = int(n**0.5)
  f = 5
  while f <= r:
    if n % f == 0: return False
    if n % (f+2) == 0: return False
    f += 6
  return True

# @TODO Actually verify the ID doesn't exist in the databse
def check_unique_id():
    return True

# /member_id/validate [GET, POST] HTML Endpoint
# ● Write a simple HTML view with a form that takes a Member ID and validates
# whether it is a valid Member ID generated by the mechanism in the previous task.
# ● Return a descriptive error message if the Member ID is not valid.
# ● Return a success message if the Member ID is valid.
# ● No need to spend too much time styling this. Plain HTML is fine. Minimal styling encouraged.
@app.route('/member_id/validate', methods=['GET','POST'])
def validate_id():
    if request.method == 'POST':
        member_id = request.form.get('member_id', None)
        print(member_id)
        response = {}
        is_valid = validate_member_id(member_id)
        if is_valid:
            response["success"] = True
            response["message"] = "Welcome back."
        else:
            response["success"] = False
            response["message"] = "Invalid Member ID. Should be a 10-digit integer of the format AAABBBCCCC, where AAA, BBB, and CCCC are each prime numbers."

        return jsonify(response)
    if request.method == 'GET':
        return "<h1>Validate Member ID</h1><form action=\"/member_id/validate\" method=\"post\"><label for=\"member_id\">Member Id</label><input type=\"number\" name=\"member_id\" /><input type=\"submit\">"

# Checks that the ID satisfies our arithmetic test
def validate_member_id(member_id):
    if int(member_id) < 100000000 or int(member_id) > 9999999999:
        return False
    num_a = int(str(member_id)[:3])
    num_b = int(str(member_id)[3:6])
    num_c = int(str(member_id)[6:])
    print(f"{num_a}-{num_b}-{num_c}")
    is_valid = (is_prime(num_a)) and (is_prime(num_b)) and (is_prime(num_c))
    print(is_valid)
    return is_valid

@app.route('/')
def index():
    return "<h1>Demo API V1</h1><ul><li><a href=\"/member_id\">Issue Member ID [POST]</a></li><li><a href=\"/member_id/validate\">Validate Member ID [GET,POST]</a></li></ul>"

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)
