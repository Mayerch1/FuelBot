# FuelBot

This bot can be used to calculate the fuel usage during a race and is compatible with any sim which allows you to read out your fuel usage.

![Fuel Results](https://imgur.com/7byL2ke.png)

There are two operation modes
* time limited races (e.g. GT classes) 
* lap limited races (e.g. Formula classes)

The bot will not require any discord permissions, [invite here](https://discord.com/api/oauth2/authorize?client_id=890731736252686337&permissions=0&scope=bot%20applications.commands)


## How to use

Simply start invoking the slash command for this bot `/fuel time` or `/fuel usage` and fill in all the required parameters.
The `/help` command lists the available commands.


![Create Fuel Calculation](https://imgur.com/KuMKpqP.png)


## Parameters

The commands are using following parameters



|Parameter| Explanation|
|---|---|
|```length```  | length of the race, format is hh:mm or minutes (mm)| 
|```laps``` | the amount of laps driven in the race|
||
|```laptime``` | your estimated avg. laptime, format is mm:ss.fff (you can leave out mm and/or fff)|
|```fuel_usage``` | the fuel you are approx. using, in liters/lap|
|```reserve_laps``` | optional, used to determin the `Safe Fuel` value, defaults to 3|



## Some users cannot use the bot?


### Permissions
Make sure the user has sufficient permission to execute **Application Commands** (`slash-commands` in earlier versions).
This permission can be used to restrict access to bots, but is usually enabled for @everyone by default

![Slash Permissions](https://imgur.com/3BGMlVl.png)

### User Settings
If the permissions are all set, but certain users are still not able to use slash-commands, the discord application might be setup incorrectly. Tell the affected user(s) to open their `user settings` and navigate to the `Text & images` section.

In the lower part of said settings page, you can find an option to toggle the usage of slash-commands.
![Slash User Settings](https://imgur.com/lI5QRoT.png)



Make sure the user has the permission to `Use Application commands`.
This is a recently introduced discord permission, and can control the access to bot commands.
By default `@everyone` is allowed to use `slash`-commands.


## More Help

Join the support server https://discord.gg/Xpyb9DX3D6 for more help


## Attributions

The Icon is created by [Arun Thomas](https://www.iconfinder.com/arunxthomas) and published under [CC-BY 3.0](https://creativecommons.org/licenses/by/3.0/)