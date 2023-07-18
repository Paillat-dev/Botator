# Botator
Botator is a discord bot that binds [@openai](https://github.com/openai) 's chat-GPT AI with [@discord](https://github.com/discord). It also has images recognition and moderation features! 
![discord com_channels_1021872219888033903_1046119234033434734](https://user-images.githubusercontent.com/75439456/204105583-2abb2d77-9404-4558-bd3e-c1a70b939758.png)

# Adding the bot to your discord server
In order to add the bot to your discord server, you will need  an OpenAI API key. You can create an account and take one [here](https://beta.openai.com/account/api-keys). **Please note that you'll have 5$ free credits (it's really a lot) when creating your account. They will be slowly used, and will expire 3 months after you created your accound, and when they have all been used or expired, you'll need to buy new tokens. You can check your tokens usage [here](https://beta.openai.com/account/usage).**

When adding the bot to your server you agree to our [privacy policy](https://github.com/Paillat-dev/Botator/blob/main/privacypolicy.md) and our [terms of service](https://github.com/Paillat-dev/Botator/blob/main/tos.md)

You can add the bot to your server by clicking [**here**](https://discord.com/api/oauth2/authorize?client_id=1046051875755134996&permissions=414669339840&scope=bot). **PLEASE NOTE THAT WE ARE NOT RESPONSIBLE FOR ANY MISUSE YOU'LL DO WITH THE BOT..**

# Setting up the bot
Run the following commands to set your bot up:

First **/setup**, define the channel you want the bot to talk into and your OPENAI api key.

Then, **/enable** to enable the bot.

Then, if you want, **/advanced** to define some more advanced parameters, and if you want to enable image recognition, **/images** to enable it. You can also enable the moderation feature by doing **/moderation**.

You can always disable the bot by doing **/disable** and delete your api key from our server by doing **/delete**.

Please note that we can possibly log the messages that are sent for **no more than 24h**, and that we will store your openai API key. You can always delete your API key from our servers by doing **/delete**. Please note that this action is irreversible.

You can now enable your bot by doing **/enable**.

You can always disable the bot by doing **/disable** and delete your api key from our server by doing **/delete**.
# Docker
You can run this bot with docker. First clone this repository. Now add your secret avlues, like the discord token in a file called .env. Finally, run the following: 

`docker compose up -d`

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

*/moderation* - Set the AI moderation settings

*/get_toxicity* - Get the toxicity that the AI would have given to a given message

*/images* - Set the AI image recognition settings

# Support me
You can support me by getting Botator premium, or donating [here](https://www.buymeacoffee.com/paillat). More informations about botator premium here below:

### Why?
At the beginning, Botator was just a project between friends, but now many people are using it, so we need something to pay for our servers. Premium is also a way to support us and our work.
### Is this mandatory?
Not at all! You can still continue using botator for free, but in order to limit our servers overload, we limit your requests at 500 per server per day.

### What are my advantages with premium?
With premium, we will increase the maximal number of requests to 5000 for the server of your choice. You will also have access to exclusive Discord channels and get help if you want to self-host Botator. You will also be able to use the image recognition feature.

### Am I going to have unlimited tokens with premium?
No! With premium, Botator will still use tokens from YOUR OpenAI account, but you will be able to use it 5000 times per day instead of 500.

### How much doe it cost?
Premium subscription costs 1$ per month.

### How can I get premium?
First join our discord server [here](https://discord.gg/pB6hXtUeDv).

Then subscribe to botator premium by clicking here:

<a href="https://www.buymeacoffee.com/paillat"><img src="https://img.buymeacoffee.com/button-api/?text=Get botator premium&emoji=&slug=paillat&button_colour=5F7FFF&font_colour=ffffff&font_family=Inter&outline_colour=000000&coffee_colour=FFDD00" /></a>

Then, link your discord account to BuyMeACoffe by following [these instructions](https://help.buymeacoffee.com/en/articles/4601477-how-do-i-access-my-discord-role).
After that you will normally be able to access some new channels in our discord server. In the Verify Premium channel, run the /premium_activate command and give your server's ID. You can learn about how to get your server's ID by clicking [here](https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-). If you have any question, you can ask here: [help-getting-premium](https://discord.com/channels/1050769643180146749/1050828186159685743).

# ToDo
- [x] add image recognition
- [x] When chatgpt API is released, add that api instead of davinci-003
- [x] Publish a GOOD docker image on dockerhub and add some more instructions about how to selfhost
- [x] Add a log and updates channel option and a way for devs to send messages to that channel on all servers.
- [x] Add moderation.
- [x] Add TOKENS warnings (when setting the bot up, people dosen't understand tha ot uses their tokens)
- [x] Add a /continue command - you know
- [x] Add DateHour in prompts
- [x] Add /redo
- [x] Add uses count reset after 24h
- [x] Organize code in COGs
- [x] add way to consider the answers to the bot's messages. 
