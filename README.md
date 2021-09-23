# FuelBot

This bot can be used to calculate the fuel usage during a race and is compatible with any sim

There are two operation modes, for races which are limited by time (e.g. GT classes) or races limited by the laps driven (like Formula classes)


## How to use

Simply start invoking the slash command for this bot `/fuel time` or `/fuel usage` and fill in all the required parameters.
The `/help` command lists the available commands.


## Parameter

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

<img src="https://imgur.com/3BGMlVl.png" alt="Create Reminder">

### User Settings
If the permissions are all set, but certain users are still not able to use slash-commands, the discord application might be setup incorrectly. Tell the affected user(s) to open their `user settings` and navigate to the `Text & images` section.

In the lower part of said settings page, you can find an option to toggle the usage of slash-commands.
<img src="https://imgur.com/lI5QRoT.png" alt="Create Reminder">



Make sure the user has the permission to `Use Application commands`.
This is a recently introduced discord permission, and can control the access to bot commands.
By default `@everyone` is allowed to use `slash`-commands.