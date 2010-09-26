require "test/unit"

require "lib/rucksack"

class TestRucksackDoc < Test::Unit::TestCase
  def setup
    @doc = Rucksack::Doc.new("http://www.foo.org", "1002910")
    
    to_doc = Rucksack::Doc.new("http://www.bar.com", "1029104001")
    from_doc = Rucksack::Doc.new("http://www.baz.net", "1111111111")
    
    @doc.to << Rucksack::Page.new(to_doc)
    @doc.to << Rucksack::Page.new(to_doc)
    @doc.from << Rucksack::Page.new(from_doc)
    @doc.from << Rucksack::Page.new(from_doc)
  end
  
  def test_to_and_from
    puts @doc.to_xml(:indent => 2)
  end
end