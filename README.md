# Botator
Botator is a discord bot that binds openai's gpt3 AI with discord. You will be able to take the conversation with the AI into a specific channel that you created.
![discord com_channels_1021872219888033903_1046119234033434734](https://user-images.githubusercontent.com/75439456/204105583-2abb2d77-9404-4558-bd3e-c1a70b939758.png)

# Adding the bot to your discord server
In order to add the bot to your discord server, you will need  an OpenAI API key. You can create an account and take one [here](https://beta.openai.com/account/api-keys)

You can add the bot to your server by clcking [here](https://discord.com/api/oauth2/authorize?client_id=1046051875755134996&permissions=2214808576&scope=applications.commands%20bot)

Then, run the following commands to set your bot up:

First **/setup**, define the channel you want the bot to talk into and your OPENAI api key.

Then, if you want, **/advanced** to define some more advanced parameters..

Please note that we can possibly log the messages that are sent for **no more than 24h**, and that we will store your openai API key. You can always delete your API key from our servers by doing **/delete**. Please note that this action is irreversible.

You can now enable your bot by doing **/enable**.

You can always disable the bot by doing **/disable** and delete your api key from our server by doing **/delete**.

# Docker
You can run this bot with docker. First clone this repository. Now replace the text into the key.txt file that you will find into the ./Botator/docker/Build directory with your **DISCORD** API key. After that,run the following command in the /Botator/docker/Build directory.

`docker build . -t botator:latest --no-cache`

Now create a directory called `botator` where you want the database files to be stored, and run the following command into that directory to run the container.

`docker run -d --name botatordef -v **your botator folder directory**:/Botator/database botator:latest`
