#!/usr/bin/env ruby

require 'tempfile'
require 'optparse'

class File
  def self.prepend(path, string)
    Tempfile.open File.basename(path) do |tempfile|
      tempfile << string

      File.open(path, 'r+') do |file|
        tempfile << file.read
        file.pos = tempfile.pos = 0
        file << tempfile.read
      end
    end
  end

  def self.prepend_line(path, string)
    self.prepend(path, string + "\n");
  end
end

optparse = OptionParser.new do |opts|
  opts.banner = "Usage: prep_data.rb [options] <data_location>" 
end
optparse.parse!

if ARGV.length == 0
  puts optparse
  exit
end

Dir.glob(ARGV[0]+'*').each do |file|
  File.prepend_line(file, "<file="+File.basename(file)+">")
end
