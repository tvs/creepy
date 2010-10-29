#!/usr/bin/env ruby

freqs = Hash.new()

doc = ""
STDIN.each_line do |line|
  if line =~ /<file=([a-zA-Z0-9]*)>/ 
    doc = $1
  else
    words = line.split()
    words.each do |word|
      freqs[word] = Hash.new(0) unless freqs.has_key?(word)
      freqs[word][doc] += 1
    end
  end
end

fr = freqs.sort { |a, b| a[0] <=> b[0] }

fr.each do |word, doc|
  print "#{word}\t"
  doc.each do |name, freq|
    print "(#{name}:#{freq})"
  end
  puts ""
end
