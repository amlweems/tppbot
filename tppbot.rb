require 'cinch'

@@count = 0

class RNGPokemon
  include Cinch::Plugin

  def initialize(*args)
    super

    @ident = @@count
    @@count = @@count + 1
  end

  timer 40, method: :rng
  def rng
    @channel ||= Channel("#twitchplayspokemon")
    commands = File.new('commands.txt').read.split
    type = commands.shift
    command = nil
    if type == "sample"
      command = commands.sample
    elsif type == "sequence"
      command = commands[@ident%commands.length]
    else
      # pass
    end
    if not command.nil? and not command.empty?
      @channel.send command
    end
  end
  
end

threads = []
users = File.new('users.txt')

users.read.split.each do |line|
  user, oauth = line.split("::")
  bot = Cinch::Bot.new do
    configure do |c|
      c.server = "199.9.252.26" # Twitch IRC IP
      c.nick = user
      c.realname = user
      c.user = user
      c.password = oauth
      c.messages_per_second = 20.0/30.0
      c.plugins.plugins = [RNGPokemon]
    end
  end
  sleep 0.75
  threads << Thread.new { bot.start }
end

threads.each { |thr| thr.join }