#!/usr/bin/env ruby

require 'lib/rucksack'
require 'optparse'

OPTIONS = {
  :output => $stdout,
  :output_to_file => false,
  :indent => 2
}

optparse = OptionParser.new do |opts|
  opts.banner = "Usage: rucksack.rb [options] <pid_map file>"
  
  opts.on('-o', '--output FILE', "Output resultant XML to FILE") do |file|
    OPTIONS[:output] = File.open(file, 'w')
    OPTIONS[:output_to_file] = true
  end
  
  opts.on('-i', '--indent N', Integer, "Indent N spaces", 
                "Default: #{OPTIONS[:indent]}") { |n| OPTIONS[:indent] = n }
end
optparse.parse!

docs = Rucksack::DocStore.new()
xml_opts = {:indent => OPTIONS[:indent]}

if ARGV.length == 0
  puts optparse
  exit
end

docs.import_map(ARGV[0])

OPTIONS[:output].print docs.to_xml(xml_opts)

File.close(OPTIONS[:output]) if OPTIONS[:output_to_file]