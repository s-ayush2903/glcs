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
projectName = "mrsFromCli"
projectNamespace = "stvayush"
gitlabInstance = "gitlab.com"
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

def handlePathExistence(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.mkdir(path)
    return True


def fetchArtifsForJob(jobIdNameMapping):
    pwd = os.getcwd()
    baseArtifsDir = os.path.join(pwd, "artifs")

    handlePathExistence(baseArtifsDir)

    for kee in jobIdNameMapping:
        artifsDir = os.path.join(baseArtifsDir, f"{jobIdNameMapping[kee]}Artifs")

        handlePathExistence(artifsDir)
        artiUrl = requests.get(f"{baseUrl}/jobs/{kee}/artifacts", headers=headers, stream=True)
        baseArchiveName = f"{jobIdNameMapping[kee]}Artifs"
        archiveName = os.path.join(artifsDir, f"{baseArchiveName}.zip")

        with artiUrl as gld:
            gld.raise_for_status()
            with open(archiveName, "wb") as gj:
                for chunk in gld.iter_content(chunk_size=8192):
                    gj.write(chunk)
        shutil.unpack_archive(archiveName, f"{baseArtifsDir}/{baseArchiveName}")
        print("-------------")
        print(f"Successfully fetched artifs for {jobIdNameMapping[kee]}, find the archive at {artifsDir}")

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
    jr = requests.get(f"{baseUrl}/pipelines/{pipelineId}/jobs", headers = headers)
    return {_["id"] : _["name"] for _ in jr.json()}


def pipelineForBranch(branchName):
    print(f"fetching latest successful pipeline for [ {branchName} ]")
    rex = requests.get(f"{baseUrl}/pipelines?refs=branchName&status=success", headers=headers)
    idForLatestSuccessfulPipeline = rex.json()[0]['id']

    print(f"Fetch successful! latest pipeline:\nhttps://{gitlabInstance}/{projectNamespace}/{projectName}/-/pipelines/{idForLatestSuccessfulPipeline}")
    print("Fetching jobs for it ...")

    jobsList = fetchJobsFromPipeline(idForLatestSuccessfulPipeline)

    print(jobsList)
    print("-----------")
    recordCountAndCallArtiFetching(jobsList)
    return idForLatestSuccessfulPipeline

def recordCountAndCallArtiFetching(jobIdNameMap):
    index = 1
    for _ in jobIdNameMap:
        print(f"{index}. {jobIdNameMap[_]}")
        index += 1

    print("-----------")

    numOfJobs = int(input("Enter NUMBER OF JOBS whose artifs you wanna fetch: "))

    jobsMemo = {}
    print("Enter num CORRESPONDING to job whose artif you're interested in: ")
    for _ in range(numOfJobs):
        jiid = int(input(""))
        kee = list(jobIdNameMap.keys())[jiid - 1]
        jobsMemo[kee] = jobIdNameMap[kee]
    print("Captured Inputs!\nFetching artifs ...")
    fetchArtifsForJob(jobsMemo)

def pipelineForMr(mrNo):
    # Will have to send cookies too for this request, as we do not have public API for this specific thing
    # Noooo, can do it without cookies as well :)
    rex = requests.get(f"{baseUrl}/pipelines?refs=refs/merge-requests/{mrNo}/head&status=success", headers=headers)
    idForLatestSuccessfulPipeline = rex.json()[0]['id']
    jobIdNameMap = fetchJobsFromPipeline(idForLatestSuccessfulPipeline)

    print("fetched jobs:")
    print("-------------")
    recordCountAndCallArtiFetching(jobIdNameMap)

def queryBranch(branchName: str):
    matches = []
    for _ in branches:
        if branchName in _:
            matches.append(_)
    print("Nearest matches:")
    for _ in matches:
        print(_)

repoUrl = f"https://{gitlabInstance}/{projectNamespace}/{projectName}"

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
