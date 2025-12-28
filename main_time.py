#!/usr/bin/python
"""For TimeWatch Version 5.069
Last updated at 10/May/2023"""

import argparse
import datetime
import json
import logging
import os

from dotenv import load_dotenv

import timewatch

# Load environment variables from .env file (for local development)
load_dotenv()

# Configure logging to show INFO level messages
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def parse_users():
    """
    Parse users from environment variables.
    
    Supports two formats:
    1. Single user (legacy):
       TIMEWATCH_COMPANY=11447
       TIMEWATCH_USERNAME=5
       TIMEWATCH_PASSWORD=secret
    
    2. Multiple users (JSON array):
       TIMEWATCH_USERS='[{"company": "11447", "username": "5", "password": "secret"}, {"company": "11447", "username": "6", "password": "secret2"}]'
    """
    users_json = os.getenv('TIMEWATCH_USERS')
    
    if users_json:
        try:
            users = json.loads(users_json)
            logger.info(f"Loaded {len(users)} users from TIMEWATCH_USERS")
            return users
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse TIMEWATCH_USERS JSON: {e}")
            exit(1)
    
    # Fallback to single user format
    company = os.getenv('TIMEWATCH_COMPANY')
    username = os.getenv('TIMEWATCH_USERNAME')
    password = os.getenv('TIMEWATCH_PASSWORD')
    
    if all([company, username, password]):
        logger.info("Loaded single user from individual env vars")
        return [{"company": company, "username": username, "password": password}]
    
    logger.error("Missing required environment variables!")
    logger.error("Either set TIMEWATCH_USERS (JSON array) or TIMEWATCH_COMPANY, TIMEWATCH_USERNAME, TIMEWATCH_PASSWORD")
    exit(1)


def some_func(company, username, password):

    #  parser = argparse.ArgumentParser(description='Automatic work hours reporting for timewatch.co.il')
    #
    #  parser.add_argument('company', type=int, help='Company ID')
    #  parser.add_argument('user', help='user name/id')
    #  parser.add_argument('password', help='user password')

    today = datetime.date.today()
    year = today.year
    month = today.month - 1
    
    logger.info(f"Starting timewatch fill for company={company}, user={username}")
    logger.info(f"Today's date: {today}")
    logger.info(f"Target year: {year}, Target month: {month}")
    
    if month == 0:
        month = 12
        year = year - 1
        logger.info(f"Adjusted to previous year: year={year}, month={month}")
    
    verbose = 2  # Changed from 0 to 2 for DEBUG level logging
    override = 'incomplete'
    # starttime = '09:00'
    # daysoff = ['friday', 'saturday']
    jitter = 10
    retries = 2


    #  parser.add_argument('-y', '--year', default=today.year, type=int, help='Year number to fill')
    #  parser.add_argument('-m', '--month', default=today.month, help='Month number or name')
    #
    #  parser.add_argument('-v', '--verbose', default=0, action='count', help='increase logging level')
    #
    #  parser.add_argument('-o', '--override', default='incomplete',
    #                      choices=['all', 'incomplete', 'regular'],
    #                      help='Control override behavior. all - override all '
    #                           'working days, unsafe to vacation/sick days. '
    #                           'incomplete = only override days with partial '
    #                           'records. regular - override regular days '
    #                           '(without absence reason) only')
    #
    #  parser.add_argument('-s', '--starttime', default='09:00', help='punch-in time')
    #  parser.add_argument('-d', '--daysoff', default=['friday', 'saturday'], help='''Days you're off, not working,
    # the defaults are Friday and Saturday''')
    #
    #  parser.add_argument('-j', '--jitter', default=10, type=int,
    #                      help='punching time random range in minutes.')
    #
    #  parser.add_argument('-r', '--retries', default=9, help='amount of times to retries on failed punchin')
    #
    #  args = parser.parse_args()

    verbosity_levels = [logging.WARNING, logging.INFO, logging.DEBUG]
    verbosity = min(verbose, len(verbosity_levels) - 1)
    logging_level = verbosity_levels[verbosity]
    
    logger.info(f"Verbosity level: {verbose}, Logging level: {logging_level}")

    tw = timewatch.TimeWatch(logging_level)
    # loglevel=logging_level,
    # override=args.override,
    # starttime=args.starttime,
    # jitter=args.jitter,
    # retries=args.retries,
    # daysoff=args.daysoff)

    # login = tw.login(args.company, args.user, args.password)

    logger.info("Attempting to login...")
    login = tw.login(company, username, password)
    if login == "Login failed!":
        logger.error("Login failed!")
        return ("*There was a problem logging in*.\nPlease check your user name and password and "
                "retry.\nnote - There is usually no 0 at the beginning of the ID.")
    else:
        logger.info("Login successful! Starting to edit month...")
        text = tw.edit_month(year, month)
        logger.info(f"Edit month completed. Result: {text}")
        return text


if __name__ == '__main__':
    logger.info("=== Script started ===")
    
    users = parse_users()
    
    results = []
    for i, user in enumerate(users, 1):
        company = user.get('company')
        username = user.get('username')
        password = user.get('password')
        
        if not all([company, username, password]):
            logger.error(f"User {i} missing required fields (company, username, password)")
            continue
        
        logger.info(f"=== Processing user {i}/{len(users)}: company={company}, user={username} ===")
        
        try:
            result = some_func(company, username, password)
            results.append({"user": username, "company": company, "status": "success", "result": result})
            logger.info(f"User {username} completed successfully")
        except Exception as e:
            logger.error(f"User {username} failed with error: {e}")
            results.append({"user": username, "company": company, "status": "error", "error": str(e)})
    
    logger.info(f"=== Script finished. Processed {len(results)} users ===")