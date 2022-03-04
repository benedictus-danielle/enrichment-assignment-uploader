import requests
from bs4 import BeautifulSoup as bs
import os
from inspect import currentframe, getframeinfo
from datetime import datetime

ENRICHMENT_BASE_URL = "https://enrichment.apps.binus.ac.id"
ACTIVITY_BASE_URL = "https://activity-enrichment.apps.binus.ac.id"
session = requests.session()

ENRICHMENT_LOGIN_URL = f"{ENRICHMENT_BASE_URL}/Login/Student/Login"


def getRequestVerificationToken():
    r = session.get(ENRICHMENT_LOGIN_URL)
    soup = bs(r.text, 'html.parser')
    token = soup.find('input', {"name": "__RequestVerificationToken"}).get('value')
    return token


def login():
    # Isi dengan email bimay
    username = ""

    # Isi dengan password bimay
    password = ""

    frameinfo = getframeinfo(currentframe())
    if username == "" or password == "":
        print(f"Isi username & password duls di line {frameinfo.lineno- 5} & {frameinfo.lineno - 2}")
        exit(0)

    token = getRequestVerificationToken()
    data = {
        "login.Username": username,
        "login.Password": password,
        "__RequestVerificationToken": token,
        "btnLogin": "Login"
    }
    r = session.post(f"{ENRICHMENT_BASE_URL}/Login/Student/DoLogin", data)


def goToActivityEnrichment():
    login()
    session.get(f"{ENRICHMENT_BASE_URL}/Login/Student/SSOToActivity")


def getAssignment():
    r = session.post(f"{ACTIVITY_BASE_URL}/Assignment/GetAssignment")
    return r.json()["data"]


def getUniqueMonth(assignments):
    value = {}

    for assignment in assignments:
        value[assignment['assignmentMonthDesc']] = []

    for assignment in assignments:
        value[assignment['assignmentMonthDesc']].append({
            "id": assignment['assignmentId'],
            "name": assignment['assignmentTypeName'],
            "status": assignment['assignmentStatusName'],
            "facultySpv": assignment['mappingFacultySpvId'],
        })
    return value


def main():
    goToActivityEnrichment()
    assignments = getUniqueMonth(getAssignment())
    for index, (assignment, value) in enumerate(assignments.items()):
        print(f"{index+1}. {assignment}")
        for val in value:
            print(f"- {val['name']}: {val['status']} ({val['id']})")

    while True:
        choose = int(input("Choose month: "))
        if 1 <= choose <= len(assignments):
            break
    choose -= 1

    while True:
        title = input("Input title: ")
        if title != "":
            break

    while True:
        filename = input("Input filename: ")
        if filename != "" and os.path.exists(filename):
            break

    
    assignment = assignments[list(assignments)[choose]]
    for x in assignment:
        file = open(filename, 'rb')
        data = {
            "AssignmentID": x['id'],
            "FacultySpvId": x['facultySpv'],
            "Title": title
        }
        r = session.post(f"{ACTIVITY_BASE_URL}/Assignment/UploadAssignment", data=data, files={"file": file})
        data["Path"] = r.json()["path"]
        submit = session.post(f"{ACTIVITY_BASE_URL}/Assignment/SubmitAssignment", data=data)
        file.close()

    file = open(filename, 'rb')
    month = datetime.strptime(list(assignments)[choose], "%B")
    r = session.post(f"{ACTIVITY_BASE_URL}/MonthlyReport/SaveMonthly", data={
        "Month": month,
        "Note": title,
    }, files={
        "ReportFile": file
    })
    file.close()


if __name__ == '__main__':
    main()
