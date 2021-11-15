import os
import rtvz
import time
import requests
import shutil

"""
@param PRIVATE-TOKEN: Access token, which impersonates you on gL
       * Global => Can use all over gL
       * Accesses gL on your behalf and lets you perform _certain_ ops via cli
       * ref: https://docs.gitlab.com/ee/user/project/settings/project_access_tokens.html#creating-a-project-access-token

@param triggerToken: Job token, used to trigger pipelines on the repository
       * Repository specific => Can't be used to handle CI ops on different projects :P
       * Used for CI related ops like triggering / canceling pipelines
       * ref: https://docs.gitlab.com/ee/ci/jobs/ci_job_token.html

@param projectId: ID of the project(repository),
       * visible just below the project name on https://gitlab.com/namespace/project-slug
       * ref: https://stackoverflow.com/a/53126068
"""

headers = {
    "PRIVATE-TOKEN": rtvz.privateToken,
}

"""
This also works, as a dictionary
"""
params = {
    "token": rtvz.triggerToken,
    "ref": "md",
}

projectId = "30942561"
branches = []

baseUrl = f"https://gitlab.com/api/v4/projects/{projectId}"

def main():
    response = requests.get(
        "https://gitlab.com/api/v4/projects/14486970/repository/branches",
        headers=headers,
    )
    Mresponse = requests.get(
        "https://gitlab.com/api/v4/projects/30942561/repository/branches",
        headers=headers,
    )
    # print(params[0])

    qry = str(input("enter branch name: "))
    # for sth in response.json():
    #    branches.append(sth['name'])
    # queryBranch(qry)
    """
    @param absppln: Triggers a new pipeline on the branch specified in `params`
    @param pipelineId: Holds the ID of the same latest pipeline triggered
    @jbzz: A list of Job IDs which the pipeline triggered runs(these are used to fetch artifs when Job(s) is/are completed)
    """
    absppln = requests.post(f"{baseUrl}/trigger/pipeline", params=params)
    print(absppln.text)
    pipelineId = absppln.json()["web_url"].split("/")[-1]

    # Thanks to Hardik for helping me make this oneliner :)
    jbzz = [
        _["id"]
        for _ in requests.get(
            f"{baseUrl}/pipelines/{pipelineId}/jobs", headers=headers
        ).json()
    ]
    print(jbzz)
    print("***********")

    suffix = 1
    time.sleep(17)
    artiList = []
    for _ in jbzz:
        fileName = "arti" + str(suffix) + ".zip"
        artiUrl = requests.get(
            f"{baseUrl}/jobs/{_}/artifacts", headers=headers, stream=True
        )
        with artiUrl as gold:
            gold.raise_for_status()
            with open(fileName, "wb") as goldenObj:
                for chunk in gold.iter_content(chunk_size=8192):
                    goldenObj.write(chunk)
        artiList.append(fileName)
        suffix += 1

    ind = 1
    for _ in artiList:
        shutil.unpack_archive(_, "artiii" + str(ind))
        ind += 1

"""
--------------
REFACTOR!!!
--------------
This fn should(and will) ideally capture a map, of jobId to its name, nothing much or less!
"""
def fetchArtifsForJob(jobId, jobName):
    pwd = os.getcwd()
    artifsDir = os.path.join(pwd, "artifs")
    artiUrl = requests.get(f"{baseUrl}/jobs/{jobId}/artifacts", headers=headers, stream=True)

    """
    --------------
    FIXME
    --------------
    This'll overwrite content when downnloading arifs for multiples jobs in one go!
    """
    if os.path.exists(artifsDir):
        shutil.rmtree(artifsDir)
    os.mkdir(artifsDir)

    baseArchiveName = f"{jobName}Artifs"
    archiveName = os.path.join(artifsDir, f"{baseArchiveName}.zip")
    with artiUrl as gld:
        gld.raise_for_status()
        with open(archiveName, "wb") as gj:
            for chunk in gld.iter_content(chunk_size=8192):
                gj.write(chunk)
    shutil.unpack_archive(archiveName, f"{artifsDir}/{baseArchiveName}")
    print("-------------")
    print(f"Successfully fetched artifs for {jobName}, find the archive at {artifsDir}")
    print("-------------")

def listBranches():
    reck = requests.get(f"{baseUrl}/repository/branches", headers=headers)
    branches = [ _["name"] for _ in reck.json() ]
    print("Fetching branches...")
    print("-------------")
    ind = 1
    for _ in branches:
        print(f"{ind}: {_}")
        ind += 1
    print("-------------")
    iid = int(input("Enter the num corresponding to branch which you wish to select: "))
    print(f"Fixed target: [ {branches[iid - 1]} ] ")
    pipelineForBranch(branches[iid - 1])

def fetchJobsFromPipeline(pipelineId):
    jobs = {}
    jr = requests.get(f"{baseUrl}/pipelines/{pipelineId}/jobs", headers = headers)
    # jobsg
    for response in jr.json():
        jobs[response["id"]] = response["name"]
    return jobs


def pipelineForBranch(branchName):
    print(f"fetching latest successful pipeline for [ {branchName} ]")
    rex = requests.get(f"{baseUrl}/pipelines?refs=branchName&status=success", headers=headers)
    idForLatestSuccessfulPipeline = rex.json()[0]['id']
    jobsList = fetchJobsFromPipeline(idForLatestSuccessfulPipeline)
    print("Fetching jobs...")
    print("-----------")
    index = 1
    for _ in jobsList:
        print(f"{index}. {jobsList[_]}")
        index += 1
    print("-----------")
    numOfJobs = int(input("Enter NUMBER OF JOBS whose artifs you wanna fetch: "))

    jobId = {}
    print("Enter num CORRESPONDING to job whose artif you're interested in: ")
    for _ in range(numOfJobs):
        jiid = int(input(""))
        kee = list(jobsList.keys())[jiid - 1]
        jobId[kee] = jobsList[kee]
    print("Captured Inputs!\nFetching artifs ...")
    for _ in range(numOfJobs):
        # Refactor this fn ffs
        fetchArtifsForJob(list(jobId.keys())[_], jobId[list(jobId.keys())[_]])

def pipelineForMr(mrNo):
    # Will have to send cookies too for this request, as we do not have public API for this specific thing
    # Noooo, can do it without cookies as well :)
    rex = requests.get(f"{baseUrl}/pipelines?refs=refs/merge-requests/{mrNo}/head&status=success", headers=headers)
    idForLatestSuccessfulPipeline = rex.json()[0]['id']

    jbzz = [
        _["id"]
        for _ in requests.get(
            f"{baseUrl}/pipelines/{idForLatestSuccessfulPipeline}/jobs", headers=headers
        ).json()
    ]

    jobIdNameMap = {}
    for jobId in jbzz:
        jobIdNameMap[jobId] = requests.get(f"{baseUrl}/jobs/{jobId}", headers=headers).json()['name']

    print("fetched jobs:")
    print("-------------")
    for job in jobIdNameMap:
        print(job, jobIdNameMap[job])

    print("-------------")
    targetJob = int(input("Enter 1 to fetch artifs of Job#1 or 2 for the second one: "))
    if targetJob == 1 or targetJob == 2:
        temp = list(jobIdNameMap.keys())[targetJob - 1]
        fetchArtifsForJob(temp, jobIdNameMap[temp])
    else:
        print("invalid entry!")

def queryBranch(branchName: str):
    matches = []
    for _ in branches:
        if branchName in _:
            matches.append(_)
    print("Nearest matches:")
    for _ in matches:
        print(_)

repoUrl = "https://gitlab.com/stvayush/mrsFromCli"
def masterFn():
    print(f"Fetching list of open MRs from {repoUrl} ...")
    print("-------------")
    mrResponse = requests.get(f"{baseUrl}/merge_requests?state=opened&order_by=updated_at", headers=headers).json()
    mrIdTitleMap = {}
    for mr in mrResponse:
        mrIdTitleMap[mr['iid']] = mr['title']

    for title in mrIdTitleMap:
        print(f"{title}: {mrIdTitleMap[title]}")

    print("-------------")
    mrNum = int(input("Enter the number of mr whose latest pipeline you wish to use: "))
    if mrNum in mrIdTitleMap.keys():
        print(f"Fetching latest successful job ran on [ {mrIdTitleMap[mrNum]} | !{mrNum} ]")
        pipelineForMr(mrNum)
    else:
        print("Invalid entry!")


listBranches()
# masterFn()
# main()
