require 'builder'
require 'hpricot'

module Rucksack
  class DocStore
    attr_accessor :docs
    def initialize()
      @docs = {}
      @pages = {}
    end
  
    # Recreates the storage mapping from a map-file that maps URLs to file IDs
    # Each line of the file should contain one mapping of the following format:
    #   url => id
    # Ex:
    #   www.wikipedia.org/index.html => 1102391
    #   where 1102391 is a file on the file system in the same directory as the map file.
    def import_map(filename)
      dir = File.dirname(filename)
    
      # Collect our document mapping from our file
      f = File.open(filename, "r")
      f.each_line do |line|
        url, id = line.split(" => ")
        if url.nil? or id.nil?
          $stderr.puts "Formatting error on line #{$.}, skipping: #{line}"
        end
        @docs[url] = Doc.new(url.strip, "#{dir}/#{id.strip}")
      end
      f.close
      
      rig_map
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
    
    def rig_map
      # Loop through each document then construct links for a "to" and "from"
      # If the doc linked to does not exist within our collection already, skip it
      
      
      @docs.each do |key, val|
        links = DocStore.get_links(val.id)
        
        links.each do |url|
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
    
    def self.get_links(file)
      list = []
      doc = Hpricot.parse(File.read(file))
      doc.search("a[@href]").each do |link|
        # Filter PDFs and other extensions
        list << link.attributes['href'] unless link =~ /\.pdf$/
      end
      list
    end
  
  end
end