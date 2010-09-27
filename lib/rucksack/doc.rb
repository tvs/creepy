require 'builder'

module Rucksack
  class Doc
    attr_reader :url, :id
    attr_accessor :from, :to
  
    def initialize(url, id)
      @url = url
      @id = id
    
      @from = []
      @to = []
    end
    
    def links_to!(page)
      @to << page
    end
    
    def linked_from!(page)
      @from << page
    end
  
    def to_xml(options = {})
      builder = Builder::XmlMarkup.new(options)
      builder.doc(:url => @url, :id => @id) do |b|
        initial = options[:margin].nil? ? 2 : options[:margin] + 2
        indented = options.merge({:margin => initial})
        b.from do |f|
          @from.each {|frm| b << frm.to_xml(indented) }
        end
      
        b.to do |t|
          @to.each {|to| b << to.to_xml(indented) }
        end
      end
    end
  
  end
end