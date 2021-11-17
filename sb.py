from dotenv import dotenv_values
import time
import reqs
import rtvz
import logging
import os
import slack
from flask import Flask
from slack.errors import SlackApiError
from slackeventsapi import SlackEventAdapter

capp = Flask(__name__)

config = dotenv_values(".env")
signingKey = config["ssigningKey"]
botToken = config["botToken"]

# For slash is must
slack_event_adapter = SlackEventAdapter(signingKey, "/slack/events", capp)
slackClient = slack.WebClient(token=botToken)

botId = slackClient.api_call("auth.test")["user_id"]


@slack_event_adapter.on("app_mention")
def handleMentions(payload):
    print(payload)
    done = False
    mentionEvent = payload["event"]
    heroId = mentionEvent["user"]
    messageId = mentionEvent["ts"]
    print("----------------------------------")
    print(f"heroId: {heroId} | botId: {botId}")
    if heroId != botId and "MR" in mentionEvent["text"] and done != True:
        done = True
        testChan = "#test"
        try:
           hangOn = reqs.masterFn()
           # slackClient.chat_postMessage(
           #     channel=testChan,
           #     text="Fetching list of OPEN MRs from the Repository, please wait...",
           # )
           slackClient.chat_postMessage(
               channel=testChan, text=str(hangOn))
           print(f"((((((((MF))))))))\n{hangOn}")
           # slackClient.chat_postMessage(
           #     channel=testChan, text=hangOn
           # )
           # print("-------------------SLEEPING-----------------")
           # time.sleep(10)
           # print("-------------------SLEPT-----------------")
           # retrievedMsgResp = slackClient.conversations_history(
           #     channel="#test", oldest=messageId, inclusive=True
           # )
           # print("00000000000000000000000000000000000000000000000000000000")
           # print(retrievedMsgResp)
           # # messageContent = reqs.baseUrl
           # print("00000000000000000000000000000000000000000000000000000000")
           # # print(mentionEvent)
           # # print(heroId)
           # print("trying to handle mentions")
        except SlackApiError as e:
            print("Encountered err==============================================")
            print(e)
    print(
        "Lulz----------------------------------------------------------------------------------------------------------"
    )
    return


@slack_event_adapter.on("xxmessage")
def message(payload):
    print("receievd message payload")
    print(payload)
    return


def postFile():
    arti = os.path.join(os.getcwd(), "artifs/secondV4onlyJobArtifs/v4.txt")
    try:
        result = slackClient.files_upload(
            channels="#btsoob",
            initial_comment="This should be visible as description @Ayush niqqa",
            file=arti,
            filetype="text",
            linknames=True,
        )
        print(result)
    except SlackApiError as e:
        print(f"err uploading file {e}")
    # logger.info(result)


def postMessage():
    print("------posting message---------")
    slackClient.chat_postMessage(channel="#test", text=f"hoiii <@{rtvz.myUid}>")


if __name__ == "__main__":
    capp.run(debug=True, port=3000)
