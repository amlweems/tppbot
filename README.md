tppbot
======

TwitchPlaysPokemon bot with good intentions

I initially created this to combat the waves of start spam in the chat, but quickly moved to allowing arbitrary input. The `commands.txt` is used to give commands. The first line specifies the type of commands  (either a pool to `sample` from or an explicit `sequence`).

To use this script, you'll need to use my modified version of cinch (Twitch doesn't fully support the IRC spec, which gives cinch some difficulties).

## Setup & Usage ##
```
git clone https://github.com/amlweems/tppbot
cd tppbot
git submodule init

# edit commands.txt and users.txt

ruby -Ilib/cinch/lib tppbot.rb
```
