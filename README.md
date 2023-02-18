# PugBot

Bot for finding groups in a discord server for World of Warcraft Mythic+ Dungeons.  



Requires `interactions.py` version `4.3.4`.  
https://discord-py-slash-command.readthedocs.io/en/latest/utils.get.html  


Usage:  

Create `#mythic-plus-pickup` in the discord server you intend to add the bot to.  
Rename `config.py.example` to `config.py`, insert your discord bot token into `token=""`, and run pugbot.py  

`/add` allows the user to join the queue as a specified role, accepts `tank`, `healer`, and `dps`.  
Users can also click the buttons at the bottom of `#mythic-plus-pickup`.  
Users will be notified when enough people have joined appropriate roles and a group is formed.
