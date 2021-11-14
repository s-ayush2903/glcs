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

    # qry = str(input("enter branch name: "))
    # for sth in response.json():
    #    branches.append(sth['name'])
    baseUrl = f"https://gitlab.com/api/v4/projects/{projectId}"
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


def queryBranch(branchName: str):
    matches = []
    for _ in branches:
        if branchName in _:
            matches.append(_)
    print("Nearest matches:")
    for _ in matches:
        print(_)


if __name__ == "__main__":
    main()
