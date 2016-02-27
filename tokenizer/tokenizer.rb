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

before do
	# The REST API always serves JSON response
  headers "Content-Type" => "application/json; charset=utf8"
end

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
	req = JSON.parse request.body.read.force_encoding("UTF-8")
	resp = {'data' => req['data'].map {|x| break_me x}}
	return resp
end