#!/usr/bin/env ruby

require 'rubygems'
require 'xml'

if ARGV.length != 2
  puts "$ validate.rb <dtd doc> <xml doc>"
  exit
end

dtd = XML::Dtd.new(File.read(ARGV[0]))

document = XML::Document.file(ARGV[1])
puts document.validate(dtd)