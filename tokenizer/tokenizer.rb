"""
Thai word breaker
@starcolon projects
"""

require 'thailang4r/word_breaker'
require 'sinatra'
require 'json'

set :port, 9861
$word_breaker = ThaiLang::WordBreaker.new	

puts "==========================="
puts "  Work tokenizer server"
puts "==========================="

def break_me(str)
	if $word_breaker.nil?
		raise 'Word breaker is not alive.'
	end
	$word_breaker.break_into_words(str)
end

get '/version/' do
	puts '0.0.1alpha'
end

post '/break/' do
	req = JSON.parse request.body.read
	puts break_me(req['word'])
end