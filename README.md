# Botator Without a Stupid Prompt

- I'm not hosting this for you but you can copy the code
- I removed the restrictions
- I don't know python but this code is shitty
- I tried to clean it up a little bit

# Adding the bot to your discord server

In order to add the bot to your Discord server, you will need an OpenAI API key, and a Discord Application API Key.

## Discord

I'm learning this as I type.

1. Go here: <https://discord.com/developers/applications/>
2. Create a new application.
3. Grab public key and put it in .env
4. Replace client_id with your Application ID: <https://discord.com/api/oauth2/authorize?client_id=1058166834068725791&permissions=2214808576&scope=applications.commands%20bot>

## OpenAPI

You get $18 for free when you sign up, which lasts quite a while.

You can create an account and grab API Key [here](https://beta.openai.com/account/api-keys).
For some reason the original author came up with, you set OpenAI's API Key up through Discord, but you set the Discord API Key in a key.txt file. Who knows.

# Docker

You can run this bot with docker. First clone this repository. Now add a key.txt in the ./Botator/docker/Build directory with your **DISCORD** API key. After that,run the following command in the /Botator/docker/Build directory.

`docker build . -t botator:latest --no-cache`

Now create a directory called `botator` where you want the database files to be stored, and run the following command into that directory to run the container.

```
docker run -d --name botator -v <your botator folder directory>:/Botator/database botator:latest
```

Then, run the following commands to set your bot up:

First **/setup**, define the channel you want the bot to talk into and your OPENAI api key.

Then, if you want, **/advanced** to define some more advanced parameters..)

You can now enable your bot by doing **/enable**.

You can always disable the bot by doing **/disable** and delete your api key from our server by doing **/delete**.

# Commands reference

*/setup* - Setup the bot

*/enable* - Enable the bot

*/disable* - Disable the bot

*/advanced* - Set the advanced settings

*/advanced_help* - Get help about the advanced settings

*/enable_tts* - Enable the Text To Speech

*/disable_tts* - Disable the Text To Speech

*/delete* - Delete all your data from our server

*/cancel* - Cancel the last message sent by the bot

*/default* - Set the advanced settings to their default values

*/redo* - Redo the last answer

*/help* - Show this command list

# ToDo

- write good code
