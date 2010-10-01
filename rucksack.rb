#!/usr/bin/env ruby

require 'lib/rucksack'
require 'optparse'

OPTIONS = {
  :output => $stdout,
  :output_to_file => false,
  :indent => 2,
  :append_to_store => "",
  :delimiter => "=>"
}

optparse = OptionParser.new do |opts|
  opts.banner = "Usage: rucksack.rb [options] <pid_map file>"
  
  opts.on('-o', '--output FILE', "Output resultant XML to FILE") do |file|
    OPTIONS[:output] = File.open(file, 'w')
    OPTIONS[:output_to_file] = true
  end
  
  opts.on('-i', '--indent N', Integer, "Indent N spaces", 
                "Default: #{OPTIONS[:indent]}") { |n| OPTIONS[:indent] = n }
                
  opts.on('-a', '--append DIR', String, "Append DIR to the pid_map path") do |d| 
    OPTIONS[:append_to_store] = d
  end
  
  opts.on('--delimiter DEL', String, "pid_map uses a delimiter DEL to separate URL and ID",
                "Default: \"#{OPTIONS[:delimiter]}\"") { |d| OPTIONS[:delimiter] = d }
end
optparse.parse!

if ARGV.length == 0
  puts optparse
  exit
end

docs = Rucksack::DocStore.new(ARGV[0], OPTIONS[:delimiter], OPTIONS[:append_to_store])
xml_opts = {:indent => OPTIONS[:indent]}

OPTIONS[:output].print docs.to_xml(xml_opts)

OPTIONS[:output].close if OPTIONS[:output_to_file]