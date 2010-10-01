module Parser
  class OutOfBoundsError < Exception; end
  class XML_Comment_Error < Exception; end
  class XML_PI_Error < Exception; end
  class XML_Reserved_Name < Exception; end
  class XML_Syntax_Error < Exception; end

  class Parser
    # XML Parser based heavily from libxml2
    # TODO: readers
    attr_accessor :index, :eof_index, :content, :line
    
    def initialize(file)
      @line = 0
      @index = 0
      @file = file
      @content = File.read(file)
      @eof_index = @content.length - 1
    end
  
  
    # TODO: PRIVATE
    # Returns the current character in the string
    # TODO: Find a better place to make this check. Having to check each query is expensive
    def cur
      if @index > @eof_index
        raise OutOfBoundsError, "Index #{index} out of bounds" 
        return nil
      end
      @content[@index].chr
    end
  
    # Returns the current + i'th character in the string
    # TODO: Find a better place to make this check. Having to check each query is expensive
    def nxt(i)
      if @index + i > @eof_index
        raise OutOfBoundsError, "Index #{@index+i} out of bounds"
        return nil
      end
      @content[@index+i].chr
    end
  
    # Compares the string character-by-character from the current index with another string.
    # Slices the content from @index...@index+str.length
    # i.e. 
    #   "helloworld".cmp("hello") => true
    #   "hel".cmp("hello") => false
    #
    def cmp(str)
      slc = @content.slice(@index...@index+str.length)
      slc == str
    end
  
    # Skips the index forward i number of characters
    def skip(i=1)
      # Looping so we can track line numbers. Maybe we should just add i.
      i.times { @index += 1; @line += 1 if cur == "\n" }
    end
    
    # skip_blank
    # skip XML whitespace
    #
    # [3] S ::= (#x20 | #x9 | #xD | #xA)+
    #
    def skip_blank()
      c = cur[0]
      while (c == 0x20 || c == 0x9 || c = 0xD || c = 0xA)
        skip
        c = cur[0]
      end
    end
    
    # is_blank?
    # returns true if cur is a blank char
    def is_blank?
      c = cur[0]
      return c == 0x20 || c == 0x9 || c = 0xD || c = 0xA
    end
    
    # is_char?
    # returns true if cur is a valid char
    def is_char?
      c = cur[0]
      return (((0x9 <= (c)) && ((c) <= 0xA)) || ((c) == 0xD) || (0x20 <= (c)))
    end
    
    # xmlParseComment:
    # Skip an XML comment
    # For compatibility, the string "--" (double-hyphen) must not occur within comments.
    #
    # [15] Comment ::= '<!--' ((Char - '-') | ('-' (Char - '-')))* '-->'
    #
    def xmlParseComment()
      return unless cmp('<!--') # Check that there is a comment right here
      skip(4)
      begin
        until (cmp("-->"))
          raise XML_Comment_Error, "Line #{@line}: '--' must not occur within comments" if cmp("--")
          skip # Skip forward until we find a closing brace
        end
        skip(3) # Skip the "-->"
      rescue OutOfBoundsError
        raise XML_Comment_Error, "Comment not terminated"
      end
    end
  
    # xmlParsePI:
    # parse an XML processing instruction
    #
    # [16] PI ::= '<?' PITarget (S (Char* - (Char* '?>' Char*)))? '?>'
    #
    def xmlParsePI()
      if (cmp('<?')) # Verify that we're entering a PI
        skip(2)
        target = xmlParsePITarget()
        
        raise XML_Syntax_Error, "Line #{@line}: PI #{target}, whitespace expected" if !is_blank?
        
        skip_whitespace()
        begin
          while (is_char? && !cmp("?>"))
            skip
          end
          skip(2) # Skip the "?>"
        rescue OutOfBoundsError
          raise XML_PI_Error, "PI #{target} never terminated"
        end
      end
    end
    
    # xmlParsePITarget
    # parse the name of a PI
    # 
    # [17] PITarget ::= Name - (('X' | 'x') ('M' | 'm') ('L' | 'l'))
    #
    def xmlParsePITarget()
      name = xmlParseName()
      if (!name.nil? && name.downcase.slice(0..2) == "xml")
        if name.length > 3
          raise XML_Reserved_Name, "Line #{@line}: Invalid name prefix 'xml'"
        else
          raise XML_Reserved_Name, "Line #{@line}: XML declaration only allowed at the start of the document"
        end
      end
      
      if (name.include?(":"))
        raise XML_Syntax_Error, "Line #{@line}: Colons are forbidden from PI names:\n #{@line}: '#{name}'"
      end
      return name
    end
    
    # xmlParseName:
    # parse an XML name.
    #
    # [4] NameChar ::= Letter | Digit | '.' | '-' | '_' | ':' |
    #                  CombiningChar | Extender
    #
    # [5] Name ::= (Letter | '_' | ':') (NameChar)*
    #
    # [6] Names ::= Name (#x20 Name)*
    #
    # Returns the Name parsed or NULL
    def xmlParseName()
      c = cur[0]
      if (((c >= 0x61) && (c <= 0x7A)) || ((c >= 0x41) && (c <= 0x5A)) || 
         (c == '_') || (c == ':')) then
         
        i = 0
        while (((c >= 0x61) && (c <= 0x7A)) || ((c >= 0x41) && (c <= 0x5A)) ||
       	       ((c >= 0x30) && (c <= 0x39)) || (c == '_') || (c == '-') ||
       	       (c == ':') || (c == '.'))
       	  i += 1
       	  c = nxt(i)[0]
       	  puts i, c.chr
     	  end
     	  
     	  if ((c > 0) && (c < 0x80))
     	    count = i - @index
     	    s = @content.slice(@index...@index+i)
     	    skip(i)
     	    return s
   	    end  
    	end 
    	return nil
    end
    
    # xmlParseTextDecl
    # parse an XML declaration header for external entities
    #
    # [77] TextDecl ::= '<?xml' VersionInfo? EncodingDecl S? '?>'
    #
    def xmlParseTextDecl()
      if (cmp("<?xml"))
        skip(5)
        raise XML_Syntax_Error, "Line #{@line}: whitespace expected after '<?xml'" if !is_blank?
      end
    end
    
    # xmlParseVersionInfo()
    # parse the XML version
    #
    # [24] VersionInfo ::= S 'version' Eq (' VersionNum ' | " VersionNum ")
    #
    # [25] Eq ::= S? '=' S?
    #
    # Returns the version string or nil
    def xmlParseVersionInfo()
      version = nil
      if (cmp("version"))
        skip(7)
        skip_blank
        
        raise XML_Syntax_Error, "Line #{@line}: '=' expected after 'version'" if (cur != '=')
        skip # Skip the '='
        skip_blank
        
        if (cur = "\"")
          skip # Skip the '\""
          version = xmlParseVersionNum()
          raise XML_Syntax_Error, "Version number string not closed" if (cur != "\"")
          skip
        elsif (cur = "\'")
          skip # skip the "\'"
          version = xmlParseVersionNum()
          raise XML_Syntax_Error, "Version number string not closed" if (cur != "\'")
          skip
        else
          raise XML_Syntax_Error, "Line #{@line}: Version number string not started, expected \" or \'"
        end
      end
      return version
    end
    
    def xmlParseVersionNum()
    end
    
    def xmlParseEncodingDecl()
    end
    
  end
  
  class DTDParser < Parser
    
    def xmlParseMarkupDecl()
      @index = 0
    end
  
    def xmlParseElementDecl()
    end
  
    def xmlParseAttributeDecl()
    end
  
    def xmlParseEntityDecl()
    end
  
    def xmlParseNotationDecl()
    end
  end
  
  class XMLParser < Parser
  end
  
end