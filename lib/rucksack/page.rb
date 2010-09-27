require 'builder'

module Rucksack
  class Page
    def initialize(doc)
      @doc = doc
    end
    
    def to_xml(options = {})
      builder = Builder::XmlMarkup.new(options)
      builder.page :url => @doc.url, :id => @doc.id
    end
    
  end
end