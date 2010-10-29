#!/usr/bin/env ruby

class Word
  def initialize(word)
    @word = word
    @docs = Hash.new(0)
    @count = 0
  end

  def add(doc, count=1)
    @count += count
    @docs[doc] += count
  end

  def to_s
    string = "#{@word}:#{@count}:"
    docs = @docs.sort { |a,b| a[1] <=> b[1] }
    docs.each { |doc, freq| string += "(#{doc},#{freq}) " }
    string
  end
end


freqs = {}

STDIN.each_line do |line|
  docs = line.split(' ')
  word = docs.shift
  
  freqs[word] = Word.new(word) unless freqs.has_key?(word)
  docs.each do |ln|
    if ln =~ /\(([a-zA-Z0-9]*):([0-9]*)\)/
      freqs[word].add($1, $2.to_i)
    end
  end
end

freqs.sort.each do |item|
  puts item[1].to_s
end
