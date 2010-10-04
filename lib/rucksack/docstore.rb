require 'builder'
require 'hpricot'

module Rucksack
  class DocStore
    attr_accessor :docs
    def initialize(filename, delimiter, append_to_path = "")
      @pid_map = filename
      @delimiter = delimiter
      @dir = File.dirname(@pid_map) + "/"
      if append_to_path.length > 0
        @dir = @dir + "#{append_to_path}/"
      end
      @docs = {}
      @pages = {}
      
      import_map()
    end
  
    # Recreates the storage mapping from a map-file that maps URLs to file IDs
    # Each line of the file should contain one mapping of the following format:
    #   url => id
    # Ex:
    #   www.wikipedia.org/index.html => 1102391
    #   where 1102391 is a file on the file system in the same directory as the map file.
    def import_map()
      # Collect our document mapping from our file
      f = File.open(@pid_map, "r")
      f.each_line do |line|
        url, id = line.split(@delimiter)
        if url.nil? or id.nil?
          $stderr.puts "Formatting error on line #{$.}, skipping: #{line}"
        end
        url.strip!
        id.strip!
        @docs[url] = Doc.new(url, id)
      end
      f.close
      
      rig_map
    end
    
    def rig_map
      # Loop through each document then construct links for a "to" and "from"
      @docs.each do |key, val|
        links = DocStore.get_links(@dir + val.id)
        
        links.each do |url|
          # If the doc linked to does not exist within our collection already, skip it
          if @docs.has_key?(url)
            # Create the new 'page' version of our doc if it doesn't already exist
            @pages[url] ||= Page.new(@docs[url])
            # Add it to our 'to' list
            val.to << @pages[url]
            
            # Create the new 'page' version of our key if it doesn't already exist
            @pages[key] ||= Page.new(val)
            # Add that to the other page's 'from' list
            @docs[url].from << @pages[key]
          end
        end  
      end
    end
    
    def to_xml(options = {})
      builder = Builder::XmlMarkup.new(options)
      builder.instruct!
      builder.docstore do |x|
        # Make sure these get indented
        initial = options[:margin].nil? ? 1 : options[:margin] + 1
        @docs.each_value { |doc| x << doc.to_xml(options.merge({:margin => initial})) }
      end
    end
    
    def self.get_links(file)
      list = []
      begin
        doc = Hpricot.parse(File.read(file))
        doc.search("a[@href]").each do |link|
          list << link.attributes['href']
        end
      rescue Exception => e
        $stderr.puts "Oh god error in #{file}"
      end      
      list
    end
  end
end