require 'cinch'

@@interval = 0.4
@@offset = 40
@@waiting = false 
@@count = 0

class RNGPokemon
  include Cinch::Plugin

  def initialize(*args)
    super
  end

  listen_to :activate_timer, method: :rng

  def listen(m, id)
    @ident = id
    sleep @@interval*@ident
    # @timer = Timer(@@offset, method: :rng)
  end

  def rng(m, id)
    @ident = id
    sleep @@interval*@ident

    @channel ||= Channel("#twitchplayspokemon")
    while true
      
      commands = File.new('commands.txt').read.split("\n")
      type, interval = commands.shift.split(" ")

      if @@waiting == false
        interval = interval.to_f
        if interval > 0 and interval != @@interval
          puts "#{Time.now.to_s} :: #{@ident} found a new interval"
          @@waiting = true
          @@pinterval = @@interval
          @@interval = interval
          @@sentinel = @ident
        end
      end
      if @@waiting
        if @ident == (@@sentinel - 1) % (@@count)
          @@waiting = false
        end
        puts "#{Time.now.to_s} :: #{@ident} waiting"
        sleep @@pinterval*(@@count - @ident - 1)
        sleep @@interval*@ident
      end

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

      sleep @@offset
    end
  end
  
end

threads = []
bots = []
users = File.new('users.txt')

users.read.split("\n").each do |line|
  user, oauth = line.split("::")
  user.strip!
  puts user
  puts oauth
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
  threads << Thread.new { bot.start }
  bots << bot
  @@count += 1
end

sleep(@@count/10.0)
bots.each_with_index do |bot, index|
  bot.handlers.dispatch(:activate_timer, nil, index)
end

threads.each { |thr| thr.join }
