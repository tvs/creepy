require 'pathname'
require 'rubygems'

module Rucksack
  VERSION = '0.0.1'
end

this_dir = Pathname.new(File.dirname(__FILE__))

%w(
  doc
  docstore
  page
).each do |name|
  require this_dir + "rucksack/#{name}"
end