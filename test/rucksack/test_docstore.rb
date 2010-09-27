require "test/unit"

require "lib/rucksack"

class TestRucksackDocStore < Test::Unit::TestCase
  def setup
    @docstore = Rucksack::DocStore.new("test/rucksack/small_storage/pid_map.dat")
    @options = {:indent => 2}
  end
  
  def test_to_xml
    @docstore.docs["http://foo.bar"] = Rucksack::Doc.new("http://foo.bar", "10221")
    
    doc = Rucksack::Doc.new("http://www.bar.com", "1029104001")
    @docstore.docs["http://foo.bar"].to << Rucksack::Page.new(doc)
    @docstore.docs["http://foo.bar"].from << Rucksack::Page.new(doc)
    puts @docstore.to_xml(@options)
  end
  
  def test_small_import
    # @docstore.import_map("test/rucksack/small_storage/pid_map.dat")
    assert_equal(3, @docstore.docs.length)
    puts @docstore.to_xml(@options)
  end
  
  def test_links
    list = Rucksack::DocStore.get_links("test/rucksack/small_storage/0")
    puts list
  end  
end